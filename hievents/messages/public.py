"""Public API related messages."""

from hievents.messages.common import EventsMessage

__all__ = ['MissingAccessToken', 'InvalidAccessToken']


class MissingAccessToken(EventsMessage):
    """Indicates that no access token was provided."""

    STATUS = 422


class InvalidAccessToken(EventsMessage):
    """Indicates that the the access token is invalid."""

    STATUS = 422
