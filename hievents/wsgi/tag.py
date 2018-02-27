"""Tag handlers."""

from his import authenticated, authorized
from wsgilib import JSON

from hievents.orm import TagList

__all__ = ['ROUTES']


@authenticated
@authorized('hievents')
def list_():
    """Lists available tags."""

    return JSON([tag.tag for tag in TagList])


ROUTES = (('GET', '/tags', list_, 'list_tags'),)
