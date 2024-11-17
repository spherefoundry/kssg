from dataclasses import dataclass, fields, field
from typing import Sequence


@dataclass
class Site:
    title: str
    base_url: str


@dataclass
class Page:
    link: str
    title: str | None = None
    page_type: str | None = None
    metadata: dict[str, any] = field(default_factory=lambda: {})


class PageList(list[Page]):
    def by_type(self, page_type: str) -> Sequence[Page]:
        for it in self:
            if it.page_type == page_type:
                yield it


@dataclass
class Context:
    site: Site
    pages: PageList = field(default_factory=PageList)
    page: Page | None = None

    def absolute_url(self, input: str) -> str:
        from urllib.parse import urljoin

        return urljoin(self.site.base_url, input)

    def render_context(self, data: dict | list | None = None) -> dict:
        ret = {f.name: getattr(self, f.name) for f in fields(self)}
        ret['absolute_url'] = lambda i: self.absolute_url(i)
        if data is not None:
            ret['data'] = data
        return ret
