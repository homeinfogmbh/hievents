"""Tag related messages."""

from hinews.messages.common import NewsMessage

__all__ = ['NoSuchTag', 'TagAdded', 'TagDeleted']


class NoSuchTag(NewsMessage):
    """Indicates that the respective tag does not exist."""

    STATUS = 404


class TagAdded(NewsMessage):
    """Indicates that the respective tag was successfully added."""

    STATUS = 201


class TagDeleted(NewsMessage):
    """Indicates that the respective tag was deleted successfully."""

    STATUS = 200
