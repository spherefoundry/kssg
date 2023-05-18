import os
import shutil
from dataclasses import asdict
from typing import Dict, Any, Optional

import yaml
from jinja2 import Environment
from yaml import BaseLoader

from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin

from .config import Config
from .context import Context, PostContext
from .post_filename_parser import PostFilenameParser


markdown_lib = (
    MarkdownIt()
    .use(front_matter_plugin)
)


class Item:
    def __init__(self, filename: str, config: Config, environment: Environment):
        self.config = config
        self.environment = environment
        self.filename = filename

    @property
    def src_path(self) -> str:
        return os.path.join(self.config.src_path, self.filename)

    @property
    def dst_path(self) -> str:
        return os.path.join(self.config.output_path, self.filename)

    def process(self, context: Context):
        pass

    def prepare_dst_dir(self):
        os.makedirs(os.path.dirname(self.dst_path), exist_ok=True)


class IgnoreItem(Item):
    pass


class StaticItem(Item):
    def process(self, context: Context):
        self.prepare_dst_dir()
        shutil.copyfile(self.src_path, self.dst_path)


class TemplateItem(Item):
    def process(self, context: Context):
        template = self.environment.get_template(self.filename)
        page = template.render(asdict(context))
        self._save_page(page)

    def _save_page(self, page: str):
        self.prepare_dst_dir()
        with open(self.dst_path, "w") as fp:
            fp.write(page)


class PostItem(Item):
    def __init__(self, filename: str, config: Config, environment: Environment):
        super().__init__(filename, config, environment)

        basename = os.path.basename(filename)
        name, extension = os.path.splitext(basename)
        transformer = PostFilenameParser.parse(name)
        self.link = transformer.link
        self.date = transformer.date

        front_matter = self._load_front_matter()

        self.title = front_matter["title"]
        self.short = front_matter["short"]

    @property
    def dst_path(self) -> str:
        return os.path.join(self.config.output_path, self.link[1:], "index.html")

    def process(self, context: Context):
        source = self._load_source()
        content = self._render_content(source)
        post_context = self._extend_context(context, content)
        page = self._render_page(post_context)
        self._save_page(page)

    def _extend_context(self, context: Context, content: str) -> PostContext:
        post = next((x for x in context.posts if x.filename == self.filename), None)
        return PostContext.from_context(context, post, content)

    def _render_content(self, markdown: str) -> str:
        content = markdown_lib.render(markdown)
        return content

    def _render_page(self, post_context: PostContext) -> str:
        template = self.environment.get_template('_post.html')
        page = template.render(asdict(post_context))
        return page

    def _save_page(self, page: str):
        self.prepare_dst_dir()
        with open(self.dst_path, "w") as fp:
            fp.write(page)

    def _load_source(self) -> str:
        with open(self.src_path, "r") as f:
            return f.read()

    def _load_front_matter(self) -> Optional[Dict[str, Any]]:
        source = self._load_source()

        tokens = markdown_lib.parse(source)
        for token in tokens:
            if token.type != 'front_matter':
                continue

            return yaml.load(token.content, BaseLoader)

        return None

    @classmethod
    def is_name_valid(cls, name: str) -> bool:
        parser = PostFilenameParser.parse(name)
        return parser is not None
