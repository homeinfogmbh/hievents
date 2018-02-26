"""Image related messages."""

from hievents.messages.common import EventsMessage

__all__ = [
    'NoSuchImage',
    'NoImageProvided',
    'NoMetaDataProvided',
    'ImageAdded',
    'ImageDeleted',
    'ImagePatched']


class NoSuchImage(EventsMessage):
    """Indicates that the respective image does not exist."""

    STATUS = 404


class NoImageProvided(EventsMessage):
    """Indicates that no image was provided during POST request."""

    STATUS = 422


class NoMetaDataProvided(EventsMessage):
    """Indicates that no meta data was provided during POST request."""

    STATUS = 422


class ImageAdded(EventsMessage):
    """Indicates that the image was added sucessfully."""

    STATUS = 201


class ImageDeleted(EventsMessage):
    """Indicates tat the image was deleted successfully."""

    STATUS = 200


class ImagePatched(EventsMessage):
    """Indicates that the image was patched successfully."""

    STATUS = 200
