"""Customer related messages."""

from hievents.messages.common import EventsMessage

__all__ = ['NoSuchCustomer', 'CustomerAdded', 'CustomerDeleted']


class NoSuchCustomer(EventsMessage):
    """Indicates that the respective customer does not exist."""

    STATUS = 404


class CustomerAdded(EventsMessage):
    """Indicates that the respective customer was successfully added."""

    STATUS = 201


class CustomerDeleted(EventsMessage):
    """Indicates that the respective customer was deleted successfully."""

    STATUS = 200
