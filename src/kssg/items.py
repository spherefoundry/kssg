import json
import os
import shutil

from jinja2 import Environment

from .config import Config
from .context import Context, Page


class Item:
    def __init__(self, input_path: str, config: Config, environment: Environment):
        self.config = config
        self.environment = environment
        self._input_path = input_path

    def input_path(self, relative: bool) -> str:
        if relative:
            return self._input_path
        else:
            return os.path.join(self.config.src_path, self._input_path)

    def output_path(self, relative: bool) -> str:
        dirname, basename = os.path.split(self._input_path)
        name, extension = os.path.splitext(basename)
        output_path = os.path.join(dirname, f"{name}{self.output_extension(extension)}")

        if relative:
            return output_path
        else:
            return os.path.join(self.config.output_path, output_path)

    def output_extension(self, input_extension: str) -> str:
        return input_extension

    @property
    def link(self) -> str:
        output_path = os.path.join("/", self.output_path(relative=True))
        dirname, basename = os.path.split(output_path)
        if basename == 'index.html':
            return dirname
        else:
            return output_path

    @property
    def page(self) -> Page | None:
        return None

    def process(self, context: Context):
        pass

    def prepare_output_path(self):
        os.makedirs(os.path.dirname(self.output_path(relative=False)), exist_ok=True)

    def save(self, content: str):
        self.prepare_output_path()
        with open(self.output_path(relative=False), "w") as fp:
            fp.write(content)


class IgnoreItem(Item):
    pass


class StaticItem(Item):
    def process(self, context: Context):
        self.prepare_output_path()
        shutil.copyfile(
            self.input_path(relative=False),
            self.output_path(relative=False)
        )


class HTMLPageItem(Item):
    def process(self, context: Context):
        template = self.environment.get_template(self.input_path(relative=True))
        rendered = template.render(context.render_context())
        self.save(rendered)

    @property
    def page(self) -> Page | None:
        return Page(
            link=self.link
        )


class JsonPageItem(Item):
    def __init__(self, filename: str, config: Config, environment: Environment):
        super().__init__(filename, config, environment)

        source = self._load_source()

        if (template_name := source.get("template", None)) is None:
            raise Exception(f"The file at {self.input_path} is missing the mandatory template field")
        self.template_name = template_name

        if (metadata := source.get("metadata", None)) is None:
            raise Exception(f"The data template at {self.input_path} is missing the mandatory metadata section")

        if (title := metadata.get("title", None)) is None:
            raise Exception(f"The metadata section for {self.input_path} is missing the mandatory title field")

        page_type = metadata.get("type", None)

        self._page = Page(
            link=self.link,
            title=title,
            page_type=page_type,
            metadata=metadata
        )

    def process(self, context: Context):
        source = self._load_source()

        template = self.environment.get_template(self.template_name)
        rendered = template.render(context.render_context(source.get("data", None)))
        self.save(rendered)

    @property
    def page(self) -> Page | None:
        return self._page

    def output_extension(self, input_extension: str) -> str:
        return ".html"

    def _load_source(self) -> dict:
        with open(self.input_path(relative=False), "r") as fp:
            return json.load(fp)
