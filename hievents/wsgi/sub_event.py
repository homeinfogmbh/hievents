"""Sub-event handler."""

from his import DATA
from wsgilib import JSON

from hievents.messages.sub_event import NoSuchSubEvent, SubEventDeleted, \
    SubEventPatched
from hievents.orm import SubEvent

__all__ = ['ROUTES']


def get_sub_event(event, ident):
    """Returns the respective sub event."""

    try:
        return SubEvent.get((SubEvent.event == event) & (SubEvent.id == ident))
    except SubEvent.DoesNotExist:
        raise NoSuchSubEvent()


def list_():
    """List sub events of a certain event."""

    return JSON([sub_event.to_dict() for sub_event in SubEvent])


def get(ident):
    """Returns the respective sub event."""

    try:
        sub_event = SubEvent.get(SubEvent.id == ident)
    except SubEvent.DoesNotExist:
        raise NoSuchSubEvent()

    return JSON(sub_event.to_dict())


def delete(ident):
    """Deletes the respective sub_event."""

    try:
        sub_event = SubEvent.get(SubEvent.id == ident)
    except SubEvent.DoesNotExist:
        raise NoSuchSubEvent()

    sub_event.delete_instance()
    return SubEventDeleted()


def patch(ident):
    """Modifies the respective sub event."""

    try:
        sub_event = SubEvent.get(SubEvent.id == ident)
    except SubEvent.DoesNotExist:
        raise NoSuchSubEvent()

    sub_event.patch(DATA.json)
    sub_event.save()
    return SubEventPatched()


ROUTES = (
    ('GET', '/event', list_, 'list_sub_events'),
    ('GET', '/event/<int:ident>', get, 'get_sub_event'),
    ('DELETE', '/event/<int:ident>', delete, 'delete_sub_event'),
    ('PATCH', '/event/<ident>', patch, 'patch_sub_event'))
