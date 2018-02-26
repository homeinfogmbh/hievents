"""Event related messages."""

from hievents.messages.common import EventsMessage

__all__ = [
    'NoSuchEvent',
    'EventCreated',
    'EventDeleted',
    'EventPatched']


class NoSuchEvent(EventsMessage):
    """Indicates that the respective event does not exist."""

    STATUS = 404


class EventCreated(EventsMessage):
    """Indicates that the respective event was successfully created."""

    STATUS = 201


class EventDeleted(EventsMessage):
    """Indicates that the respective event was successfully deleted."""

    STATUS = 200


class EventPatched(EventsMessage):
    """Indicates that the respective event was successfully patched."""

    STATUS = 200
