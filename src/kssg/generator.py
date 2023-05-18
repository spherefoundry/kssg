import os
import shutil

from jinja2 import Environment, select_autoescape, FileSystemLoader

from .config import Config
from .context import Post, Context, Site
from .items import IgnoreItem, StaticItem, TemplateItem, PostItem, Item


class Generator:
    def __init__(self, config: Config):
        self.config = config
        self.environment = Environment(
            loader=FileSystemLoader(self.config.src_path),
            autoescape=select_autoescape()
        )

    def clean(self):
        if os.path.isdir(self.config.output_path):
            shutil.rmtree(self.config.output_path)
            os.makedirs(self.config.output_path)

    def build(self):
        items: [Item] = []
        posts: [Post] = []

        # FileSystemLoader doesn't have the knowledge necessary to distinguish between templates and non-template,
        # and so yields all files. It's up to us to decide what to do with them.
        for file_name in self.environment.list_templates():
            item = self.classify_file(file_name)
            items.append(item)

            if isinstance(item, PostItem):
                posts.append(Post.from_post_item(item))

        posts.sort(key=lambda it: it.date, reverse=True)

        context = Context(
            site=Site(deployment_domain=self.config.deployment_domain),
            posts=posts
        )

        for item in items:
            item.process(context)

    def watch(self):
        from livereload import Server

        def operation():
            self.clean()
            self.build()

        operation()
        server = Server()
        watched_globs = [
            f'{self.config.src_path}/**/*'
        ]

        for glob in watched_globs:
            server.watch(glob, operation)

        if self.config.server_open_browser_tab:
            # Open site in default browser
            import webbrowser
            webbrowser.open(f"http://{self.config.server_host}:{self.config.server_port}")

        server.serve(
            host=self.config.server_host,
            port=self.config.server_port,
            root=self.config.output_path
        )

    def classify_file(self, filename: str) -> Item:
        basename = os.path.basename(filename)
        name, extension = os.path.splitext(basename)
        dirname = os.path.dirname(filename)

        if basename.startswith("_"):
            return IgnoreItem(filename, self.config, self.environment)

        if dirname.startswith(self.config.post_dir):
            if PostItem.is_name_valid(name) and extension in self.config.posts_extensions:
                return PostItem(filename, self.config, self.environment)
            else:
                return IgnoreItem(filename, self.config, self.environment)

        if extension in self.config.template_extensions:
            return TemplateItem(filename, self.config, self.environment)

        return StaticItem(filename, self.config, self.environment)