"""Sub-event handler."""

from his import DATA
from wsgilib import JSON

from hievents.messages.sub_event import NoSuchSubEvent, SubEventCreated, \
    SubEventDeleted, SubEventPatched
from hievents.orm import SubEvent
from hievents.wsgi.event import get_event

__all__ = ['ROUTES']


def get_sub_event(event, ident):
    """Returns the respective sub event."""

    try:
        return SubEvent.get((SubEvent.event == event) & (SubEvent.id == ident))
    except SubEvent.DoesNotExist:
        raise NoSuchSubEvent()


def list_(ident):
    """List sub events of a certain event."""

    return JSON([
        sub_event.to_dict() for sub_event in get_event(ident).sub_events])


def get(event_id, sub_event_id):
    """Returns the respective sub event."""

    return JSON(get_sub_event(get_event(event_id), sub_event_id).to_dict())


def post(ident):
    """Adds a sub event."""

    event = get_event(ident)
    sub_event = SubEvent.from_dict(event, DATA.json)
    sub_event.save()
    return SubEventCreated(id=sub_event.id)


def delete(event_id, sub_event_id):
    """Deletes the respective sub_event."""

    get_sub_event(get_event(event_id), sub_event_id).delete_instance()
    return SubEventDeleted()


def patch(event_id, sub_event_id):
    """Modifies the respective sub event."""

    sub_event = get_sub_event(get_event(event_id), sub_event_id)
    sub_event.patch(DATA.json)
    sub_event.save()
    return SubEventPatched()


ROUTES = (
    ('GET', '/event/<int:ident>/sub_event', list_, 'list_sub_events'),
    ('GET', '/event/<int:event_id>/sub_event/<int:sub_event_id>', get,
     'get_sub_events'),
    ('POST', '/event/<int:ident>/sub_event', post, 'add_sub_events'),
    ('DELETE', '/event/<int:event_id>/sub_event/<int:sub_event_id>', delete,
     'delete_sub_events'),
    ('PATCH', '/event/<int:event_id>/sub_event/<int:sub_event_id>', patch,
     'patch_sub_events'))
