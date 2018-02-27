"""Endpoint functions for event management."""

from hinews.Exceptions import InvalidElements
from his import ACCOUNT, DATA, authenticated, authorized
from his.messages import MissingData, InvalidData
from peeweeplus import FieldValueError, FieldNotNullable
from wsgilib import JSON

from hievents.messages.event import NoSuchEvent, EventCreated, EventDeleted,\
    EventPatched
from hievents.orm import Event

__all__ = ['get_event', 'ROUTES']


def get_event(ident):
    """Returns the respective event."""

    try:
        return Event.get(Event.id == ident)
    except Event.DoesNotExist:
        raise NoSuchEvent()


def set_tags(event, dictionary):
    """Sets the respective tags of the event iff specified."""

    try:
        event.tags = dictionary['tags']
    except KeyError:
        return []
    except InvalidElements as invalid_elements:
        return list(invalid_elements)

    return []


def set_customers(event, dictionary):
    """Sets the respective customers of the event iff specified."""

    try:
        event.customers = dictionary['customers']
    except KeyError:
        return []
    except InvalidElements as invalid_elements:
        return list(invalid_elements)

    return []


@authenticated
@authorized('hievents')
def list_():
    """Lists all available events."""

    return JSON([event.to_dict() for event in Event])


@authenticated
@authorized('hievents')
def get(ident):
    """Returns a specific event."""

    return JSON(get_event(ident).to_dict())


@authenticated
@authorized('hievents')
def post():
    """Adds a new event."""

    dictionary = DATA.json

    try:
        event = Event.from_dict(
            ACCOUNT, dictionary, allow=('tags', 'customers'))
    except FieldNotNullable as field_not_nullable:
        raise MissingData(**field_not_nullable.to_dict())
    except FieldValueError as field_value_error:
        raise InvalidData(**field_value_error.to_dict())

    event.save()
    invalid_tags = set_tags(event, dictionary)
    invalid_customers = set_customers(event, dictionary)

    return EventCreated(
        id=event.id, invalid_tags=invalid_tags,
        invalid_customers=invalid_customers)


@authenticated
@authorized('hievents')
def delete(ident):
    """Adds a new event."""

    get_event(ident).delete_instance()
    return EventDeleted()


@authenticated
@authorized('hievents')
def patch(ident):
    """Adds a new event."""

    event = get_event(ident)
    dictionary = DATA.json
    event.patch(dictionary, allow=('tags', 'customers'))
    event.save()
    event.editors.add(ACCOUNT)
    invalid_tags = set_tags(event, dictionary)
    invalid_customers = set_customers(event, dictionary)
    return EventPatched(
        invalid_tags=invalid_tags, invalid_customers=invalid_customers)


ROUTES = (
    ('GET', '/event', list_, 'list_events'),
    ('GET', '/event/<int:ident>', get, 'get_event'),
    ('POST', '/event', post, 'post_event'),
    ('DELETE', '/event/<int:ident>', delete, 'delete_event'),
    ('PATCH', '/event/<int:ident>', patch, 'patch_event'))
