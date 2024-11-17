import functools
import os
import shutil

from jinja2 import Environment, select_autoescape, FileSystemLoader

from .config import Config
from .context import Context, Site, Page, PageList
from .items import IgnoreItem, StaticItem, HTMLPageItem, JsonPageItem, Item


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
        pages: [Page] = []

        # FileSystemLoader doesn't have the knowledge necessary to distinguish between templates and non-template,
        # and so yields all files. It's up to us to decide what to do with them.
        for file_name in self.environment.list_templates():
            item = self.classify_file(file_name)
            items.append(item)

            if (page := item.page) is not None:
                pages.append(page)

        context = Context(
            site=Site(
                title=self.config.site_title,
                base_url=self.config.site_base_url
            ),
            pages=PageList(pages)
        )

        for item in items:
            if (page := item.page) is not None:
                context.page = page
            else:
                context.page = None
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

        if basename.startswith("_"):
            return IgnoreItem(filename, self.config, self.environment)

        if extension in self.config.html_page_extensions:
            return HTMLPageItem(filename, self.config, self.environment)

        if extension in self.config.json_page_extensions:
            return JsonPageItem(filename, self.config, self.environment)

        return StaticItem(filename, self.config, self.environment)