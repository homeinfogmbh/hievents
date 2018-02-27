"""Tag handlers."""

from hinews.messages.tag import NoSuchTag, TagDeleted
from his import authenticated, authorized
from wsgilib import JSON

from hievents.orm import TagList, Tag

__all__ = ['ROUTES']


@authenticated
@authorized('hievents')
def list_():
    """Lists available tags."""

    return JSON([tag.tag for tag in TagList])


@authenticated
@authorized('hievents')
def get(ident):
    """Returns the respective tag."""

    try:
        tag = Tag.get(Tag.id == ident)
    except Tag.DoesNotExist:
        raise NoSuchTag()

    return JSON(tag.to_dict())


@authenticated
@authorized('hievents')
def delete(ident):
    """Deletes the respective tag."""

    try:
        tag = Tag.get(Tag.id == ident)
    except Tag.DoesNotExist:
        raise NoSuchTag()

    tag.delete_instance()
    return TagDeleted()


ROUTES = (
    ('GET', '/tags', list_, 'list_tags'),
    ('GET', '/tags/<int:ident>', delete, 'list_tags'))
