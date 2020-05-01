"""Endpoint functions for event management."""

from json import loads

from flask import request

from hinews.exceptions import InvalidCustomer, InvalidTag
from hinews.messages.customer import NoSuchCustomer, CustomerAdded
from hinews.messages.image import NoImageProvided, NoMetaDataProvided, \
    ImageAdded
from hinews.messages.tag import NoSuchTag, TagAdded
from his import ACCOUNT, authenticated, authorized
from his.messages import MissingData, InvalidData
from peeweeplus import FieldValueError, FieldNotNullable
from wsgilib import JSON

from hievents.messages.event import NoSuchEvent, EventCreated, EventDeleted,\
    EventPatched
from hievents.messages.sub_event import SubEventCreated
from hievents.orm import Event, Editor, Image, EventCustomer, Tag, SubEvent

__all__ = ['_get_event', 'ROUTES']


def _get_event(ident):
    """Returns the respective event."""

    try:
        return Event.get(Event.id == ident)
    except Event.DoesNotExist:
        raise NoSuchEvent()


def _get_images(event):
    """Yields the event's images."""

    return Image.select().where(Image.event == event)


def _get_event_customers(event):
    """Yields the event's customers."""

    return EventCustomer.select().where(EventCustomer.event == event)


def _get_tags(event):
    """Yields tags of the respective event."""

    return Tag.select().where(Tag.event == event)


def _get_sub_events(event):
    """Yields the event's sub events."""

    return SubEvent.select().where(SubEvent.event == event)


@authenticated
@authorized('hievents')
def list_():
    """Lists all available events."""

    return JSON([event.to_json() for event in Event])


@authenticated
@authorized('hievents')
def get(ident):
    """Returns a specific event."""

    return JSON(_get_event(ident).to_json())


@authenticated
@authorized('hievents')
def post():
    """Adds a new event."""

    try:
        event = Event.from_json(ACCOUNT, request.json)
    except FieldNotNullable as field_not_nullable:
        raise MissingData(**field_not_nullable.to_json())
    except FieldValueError as field_value_error:
        raise InvalidData(**field_value_error.to_json())

    event.save()
    return EventCreated(id=event.id)


@authenticated
@authorized('hievents')
def delete(ident):
    """Adds a new event."""

    _get_event(ident).delete_instance()
    return EventDeleted()


@authenticated
@authorized('hievents')
def patch(ident):
    """Adds a new event."""

    event = _get_event(ident)
    event.patch_json(request.json)
    event.save()
    editor = Editor.add(event, ACCOUNT)
    editor.save()
    return EventPatched()


@authenticated
@authorized('hievents')
def list_images(ident):
    """Lists all images of the respective event."""

    return JSON([image.to_json() for image in _get_images(_get_event(ident))])


@authenticated
@authorized('hievents')
def post_image(ident):
    """Adds a new image to the respective event."""

    try:
        image = request.files['image']
    except KeyError:
        raise NoImageProvided()

    try:
        metadata = request.files['metadata']
    except KeyError:
        raise NoMetaDataProvided()

    event = _get_event(ident)

    with image.stream as stream:
        image = stream.read()

    with metadata.stream as stream:
        metadata = stream.read()

    metadata = loads(metadata.decode())

    try:
        image = Image.add(event, image, metadata, ACCOUNT)
    except KeyError as key_error:
        raise MissingData(key=key_error.args[0])
    except ValueError as value_error:
        raise InvalidData(hint=value_error.args[0])

    image.file.save()
    image.save()
    return ImageAdded(id=image.id)


@authenticated
@authorized('hievents')
def list_customers(ident):
    """Lists customers of the respective event."""

    return JSON([
        event_customer.to_json() for event_customer in _get_event_customers(
            _get_event(ident))])


@authenticated
@authorized('hievents')
def post_customer(ident):
    """Adds a customer to the respective event."""

    event = _get_event(ident)

    try:
        customer = EventCustomer.from_json(event, request.json)
    except InvalidCustomer:
        raise NoSuchCustomer()

    customer.save()
    return CustomerAdded()


@authenticated
@authorized('hievents')
def list_tags(ident):
    """Lists tags of the respective event."""

    return JSON([tag.to_json() for tag in _get_tags(_get_event(ident))])


@authenticated
@authorized('hievents')
def post_tag(ident):
    """Adds a tag to the respective event."""

    event = _get_event(ident)

    try:
        tag = Tag.from_text(event, request.data.decode())
    except InvalidTag:
        return NoSuchTag()

    tag.save()
    return TagAdded()


@authenticated
@authorized('hievents')
def list_sub_events(ident):
    """Adds a tag to the respective event."""

    return JSON([sub_event.to_json() for sub_event in _get_sub_events(
        _get_event(ident))])


@authenticated
@authorized('hievents')
def post_sub_event(ident):
    """Adds a tag to the respective event."""

    event = _get_event(ident)
    sub_event = SubEvent.from_json(event, request.json)
    sub_event.save()
    return SubEventCreated()


ROUTES = (
    # Events.
    ('GET', '/event', list_, 'list_events'),
    ('GET', '/event/<int:ident>', get, '_get_event'),
    ('POST', '/event', post, 'post_event'),
    ('DELETE', '/event/<int:ident>', delete, 'delete_event'),
    ('PATCH', '/event/<int:ident>', patch, 'patch_event'),
    # Event images.
    ('GET', '/event/<int:ident>/images', list_images, 'list_event_images'),
    ('POST', '/event/<int:ident>/images', post_image, 'post_event_image'),
    # Event customers.
    ('GET', '/event/<int:ident>/customers', list_customers,
     'list_event_customers'),
    # Tags.
    ('GET', '/event/<int:ident>/tags', list_tags, 'list_event_tags'),
    ('POST', '/event/<int:ident>/tags', post_tag, 'post_event_tag'),
    # Sub-events.
    ('GET', '/event/<int:ident>/sub_event', list_sub_events,
     'list_event_sub_events'),
    ('POST', '/event/<int:ident>/sub_event', post_sub_event,
     'post_event_sub_event'))
