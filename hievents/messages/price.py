"""Price related messages."""

from hievents.messages.common import EventsMessage

__all__ = ["NoSuchPrice", "PriceCreated", "PriceDeleted", "PricePatched"]


class NoSuchPrice(EventsMessage):
    """Indicates that the respective price does not exist."""

    STATUS = 404


class PriceCreated(EventsMessage):
    """Indicates that the respective price was successfully created."""

    STATUS = 201


class PriceDeleted(EventsMessage):
    """Indicates that the respective price was successfully deleted."""

    STATUS = 200


class PricePatched(EventsMessage):
    """Indicates that the respective price was successfully patched."""

    STATUS = 200
