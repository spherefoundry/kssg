from dataclasses import dataclass, fields, asdict
from datetime import date


@dataclass
class Post:
    filename: str
    title: str
    short: str
    link: str
    date: date
    order: int
    front_matter: [any]

    @classmethod
    def from_post_item(cls, item: 'PostItem') -> 'Post':
        return Post(
            filename=item.filename,
            title=item.title,
            short=item.short,
            link=item.link,
            date=item.date,
            order=item.order,
            front_matter=item.front_matter
        )


@dataclass
class Site:
    title: str
    base_url: str


@dataclass
class Context:
    site: Site
    posts: [Post]

    def absolute_url(self, input: str) -> str:
        from urllib.parse import urljoin

        return urljoin(self.site.base_url, input)

    def render_context(self) -> dict:
        ret = asdict(self)
        ret['absolute_url'] = lambda input: self.absolute_url(input)
        return ret

@dataclass
class PostContext(Context):
    post: Post
    content: str

    @staticmethod
    def from_context(context: Context, post: Post, content: str) -> 'PostContext':
        kwargs = dict((field.name, getattr(context, field.name)) for field in fields(context))
        kwargs['post'] = post
        kwargs['content'] = content
        return PostContext(**kwargs)
