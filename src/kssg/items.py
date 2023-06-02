import os
import shutil
from typing import Dict, Any, Optional, Sequence, MutableMapping

import yaml
from jinja2 import Environment
from markdown_it.renderer import RendererHTML, Token
from yaml import BaseLoader

from markdown_it import MarkdownIt
from markdown_it.utils import OptionsDict
from mdit_py_plugins.front_matter import front_matter_plugin
from mdit_py_plugins.anchors import anchors_plugin

from .config import Config
from .context import Context, PostContext
from .post_filename_parser import PostFilenameParser


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
        page = template.render(context.render_context())
        self._save_page(page)

    def _save_page(self, page: str):
        self.prepare_dst_dir()
        with open(self.dst_path, "w") as fp:
            fp.write(page)


class PostItem(Item):
    def __init__(self, filename: str, config: Config, environment: Environment):
        super().__init__(filename, config, environment)
        self.md_renderer = self._md_renderer()

        basename = os.path.basename(filename)
        name, extension = os.path.splitext(basename)
        transformer = PostFilenameParser.parse(name)
        self.link = transformer.link
        self.date = transformer.date

        self.front_matter = self._load_front_matter()

        self.title = self.front_matter["title"]
        self.short = self.front_matter["short"]
        self.order = int(self.front_matter.get("order", "0"))

    @property
    def dst_path(self) -> str:
        return os.path.join(self.config.output_path, self.link[1:], "index.html")

    def process(self, context: Context):
        source = self._load_source()
        content = self._render_content(source, context)
        post_context = self._extend_context(context, content)
        page = self._render_page(post_context)
        self._save_page(page)

    def _extend_context(self, context: Context, content: str) -> PostContext:
        post = next((x for x in context.posts if x.filename == self.filename), None)
        return PostContext.from_context(context, post, content)

    def _render_content(self, markdown: str, context: Context) -> str:
        raw_content = self.md_renderer.render(markdown)
        ext_context = self._extend_context(context, "")
        template = self.environment.from_string(raw_content)
        content = template.render(ext_context.render_context())
        return content

    def _render_page(self, post_context: PostContext) -> str:
        template = self.environment.get_template('_post.html')
        page = template.render(post_context.render_context())
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

        tokens = self.md_renderer.parse(source)
        for token in tokens:
            if token.type != 'front_matter':
                continue

            return yaml.load(token.content, BaseLoader)

        return None

    def _md_renderer(self):
        def custom_render_fence(
                renderer: RendererHTML,
                tokens: Sequence[Token],
                idx: int,
                options: OptionsDict,
                env: MutableMapping
        ) -> str:
            return "{% raw %}\n" + renderer.fence(tokens, idx, options, env) + "\n{% endraw %}"

        markdown_lib = MarkdownIt() \
            .use(front_matter_plugin) \
            .use(anchors_plugin)
        markdown_lib.add_render_rule('fence', custom_render_fence)

        return markdown_lib

    @classmethod
    def is_name_valid(cls, name: str) -> bool:
        parser = PostFilenameParser.parse(name)
        return parser is not None
