"""Endpoint functions for event management."""

from hinews.exceptions import InvalidCustomer, InvalidTag
from hinews.messages.customer import NoSuchCustomer, CustomerAdded, \
    CustomerDeleted
from hinews.messages.image import NoImageProvided, NoMetaDataProvided, \
    ImageAdded
from hinews.messages.tag import NoSuchTag, TagAdded, TagDeleted
from his import ACCOUNT, DATA, authenticated, authorized
from his.messages import MissingData, InvalidData
from peeweeplus import FieldValueError, FieldNotNullable
from wsgilib import JSON

from hievents.messages.event import NoSuchEvent, EventCreated, EventDeleted,\
    EventPatched
from hievents.orm import Event, Image, CustomerList, EventCustomer, Tag

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


def _get_customer(cid):
    """Returns the respective customer."""

    try:
        return CustomerList.get(CustomerList.customer == cid).customer
    except CustomerList.DoesNotExist:
        raise NoSuchCustomer()


def _get_event_customers(event):
    """Yields the event's customers."""

    return EventCustomer.select().where(EventCustomer.event == event)


def _get_event_customer(event, customer):
    """Returns the respective event customer."""

    try:
        return EventCustomer.get(
            (EventCustomer.event == event)
            & (EventCustomer.customer == customer))
    except EventCustomer.DoesNotExist:
        raise NoSuchCustomer()


def _get_tags(event):
    """Yields tags of the respective event."""

    return Tag.select().where(Tag.event == event)


def _get_tag(event, tag):
    """Returns the respective tag record."""

    try:
        return Tag.get((Tag.event == event) & (Tag.tag == tag))
    except Tag.DoesNotExist:
        raise NoSuchTag()


@authenticated
@authorized('hievents')
def list_():
    """Lists all available events."""

    return JSON([event.to_dict() for event in Event])


@authenticated
@authorized('hievents')
def get(ident):
    """Returns a specific event."""

    return JSON(_get_event(ident).to_dict())


@authenticated
@authorized('hievents')
def post():
    """Adds a new event."""

    dictionary = DATA.json

    try:
        event = Event.from_dict(ACCOUNT, dictionary)
    except FieldNotNullable as field_not_nullable:
        raise MissingData(**field_not_nullable.to_dict())
    except FieldValueError as field_value_error:
        raise InvalidData(**field_value_error.to_dict())

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
    event.patch(DATA.json)
    event.save()
    event.editors.add(ACCOUNT)
    return EventPatched()


@authenticated
@authorized('hievents')
def list_images(ident):
    """Lists all images of the respective event."""

    return JSON([image.to_dict() for image in _get_images(_get_event(ident))])


@authenticated
@authorized('hievents')
def post_image(ident):
    """Adds a new image to the respective event."""

    files = DATA.files

    try:
        image = files['image']
    except KeyError:
        raise NoImageProvided()

    try:
        metadata = files['metadata']
    except KeyError:
        raise NoMetaDataProvided()

    try:
        image = _get_event(ident).images.add(
            image.bytes, metadata.json, ACCOUNT)
    except KeyError as key_error:
        raise MissingData(key=key_error.args[0])
    except ValueError as value_error:
        raise InvalidData(hint=value_error.args[0])

    return ImageAdded(id=image.id)


@authenticated
@authorized('hievents')
def list_customers(ident):
    """Lists customers of the respective event."""

    return JSON([
        event_customer.to_dict() for event_customer in _get_event_customers(
            _get_event(ident))])


@authenticated
@authorized('hievents')
def post_customer(ident):
    """Adds a customer to the respective event."""

    event = _get_event(ident)

    try:
        customer = EventCustomer.from_dict(event, DATA.json)
    except InvalidCustomer:
        raise NoSuchCustomer()

    customer.save()
    return CustomerAdded()


@authenticated
@authorized('hievents')
def delete_customer(event_id, customer_id):
    """Deletes the respective customer from the event."""

    _get_event_customer(
        _get_event(event_id), _get_customer(customer_id)).delete_instance()
    return CustomerDeleted()


@authenticated
@authorized('hievents')
def list_tags(ident):
    """Lists tags of the respective event."""

    return JSON([tag.to_dict() for tag in _get_tags(_get_event(ident))])


@authenticated
@authorized('hievents')
def post_tag(ident):
    """Adds a tag to the respective event."""

    event = _get_event(ident)

    try:
        tag = Tag.from_text(event, DATA.text)
    except InvalidTag:
        return NoSuchTag()

    tag.save()
    return TagAdded()


@authenticated
@authorized('hievents')
def delete_tag(event_id, tag):
    """Deletes the respective tag."""

    _get_tag(_get_event(event_id), tag).delete_instance()
    return TagDeleted()


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
    ('POST', '/event/<int:ident>/customers', post_customer,
     'post_event_customer'),
    ('DELETE', '/event/<int:event_id>/customers/<customer_id>',
     delete_customer, 'delete_event_customer'),
    # Tags.
    ('GET', '/event/<int:ident>/tags', list_tags, 'list_event_tags'),
    ('POST', '/event/<int:ident>/tags', post_tag, 'post_event_tag'),
    ('DELETE', '/event/<int:event_id>/tags/<tag>', delete_tag,
     'delete_event_tag'))
