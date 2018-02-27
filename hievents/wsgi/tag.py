"""Tag handlers."""

from hinews.exceptions import InvalidTag
from hinews.messages.tag import NoSuchTag, TagAdded, TagDeleted
from his import DATA, authenticated, authorized
from wsgilib import JSON

from hievents.orm import TagList
from hievents.wsgi.event import get_event

__all__ = ['ROUTES']


@authenticated
@authorized('hievents')
def list_():
    """Lists available tags."""

    return JSON([tag.tag for tag in TagList])


@authenticated
@authorized('hievents')
def get(ident):
    """Lists tags of the respective event."""

    return JSON([tag.to_dict() for tag in get_event(ident).tags])


@authenticated
@authorized('hievents')
def post(ident):
    """Adds a tag to the respective event."""

    try:
        get_event(ident).tags.add(DATA.text)
    except InvalidTag:
        return NoSuchTag()

    return TagAdded()


@authenticated
@authorized('hievents')
def delete(event_id, tag_or_id):
    """Deletes the respective tag."""

    get_event(event_id).tags.delete(tag_or_id)
    return TagDeleted()


ROUTES = (
    ('GET', '/tags', list_, 'list_tags'),
    ('GET', '/event/<int:ident>/tags', get, 'get_tags'),
    ('POST', '/event/<int:ident>/tags', post, 'post_tag'),
    ('DELETE', '/event/<int:event_id>/tags/<tag>', delete, 'delete_tag'))
