from dataclasses import dataclass, fields
from datetime import date


@dataclass
class Post:
    filename: str
    title: str
    short: str
    link: str
    date: date

    @classmethod
    def from_post_item(cls, item: 'PostItem') -> 'Post':
        return Post(
            filename=item.filename,
            title=item.title,
            short=item.short,
            link=item.link,
            date=item.date,
        )


@dataclass
class Site:
    deployment_domain: str


@dataclass
class Context:
    site: Site
    posts: [Post]


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
