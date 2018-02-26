"""Messages."""

from his import locales, Message

__all__ = ['EventsMessage']


class EventsMessage(Message):
    """A JSON-ish response."""

    LOCALES = locales('/etc/his.d/locale/hievents.ini')
    ABSTRACT = True
