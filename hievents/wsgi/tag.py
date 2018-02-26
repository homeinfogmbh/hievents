"""Tag handlers."""

from his import DATA, authenticated, authorized
from wsgilib import JSON

from hinews.messages.tag import NoSuchTag, TagAdded, TagDeleted
from hinews.orm import InvalidTag, TagList
from hinews.wsgi.article import get_article

__all__ = ['ROUTES']


@authenticated
@authorized('hinews')
def list_():
    """Lists available tags."""

    return JSON([tag.tag for tag in TagList])


@authenticated
@authorized('hinews')
def get(ident):
    """Lists tags of the respective article."""

    return JSON([tag.to_dict() for tag in get_article(ident).tags])


@authenticated
@authorized('hinews')
def post(ident):
    """Adds a tag to the respective article."""

    try:
        get_article(ident).tags.add(DATA.text)
    except InvalidTag:
        return NoSuchTag()

    return TagAdded()


@authenticated
@authorized('hinews')
def delete(article_id, tag_or_id):
    """Deletes the respective tag."""

    get_article(article_id).tags.delete(tag_or_id)
    return TagDeleted()


ROUTES = (
    ('GET', '/tags', list_, 'list_tags'),
    ('GET', '/article/<int:ident>/tags', get, 'get_tags'),
    ('POST', '/article/<int:ident>/tags', post, 'post_tag'),
    ('DELETE', '/article/<int:article_id>/tags/<tag>', delete, 'delete_tag'))
