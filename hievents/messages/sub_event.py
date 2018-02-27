"""Sub-event related messages."""

from hievents.messages.common import EventsMessage

__all__ = [
    'NoSuchSubEvent',
    'SubEventCreated',
    'SubEventDeleted',
    'SubEventPatched']


class NoSuchSubEvent(EventsMessage):
    """Indicates that the respective sub-event does not exist."""

    STATUS = 404


class SubEventCreated(EventsMessage):
    """Indicates that the respective sub-event was successfully created."""

    STATUS = 201


class SubEventDeleted(EventsMessage):
    """Indicates that the respective sub-event was successfully deleted."""

    STATUS = 200


class SubEventPatched(EventsMessage):
    """Indicates that the respective sub-event was successfully patched."""

    STATUS = 200
