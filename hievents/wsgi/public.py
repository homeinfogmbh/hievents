"""Public customer interface without
HIS authentication or authorization.
"""
from flask import request

from hinews.messages.image import NoSuchImage
from hinews.messages.public import MissingAccessToken, InvalidAccessToken
from wsgilib import JSON, Binary

from hievents.messages.event import NoSuchEvent
from hievents.orm import event_active, Event, Image, AccessToken

__all__ = ['ROUTES']


def _get_customer():
    """Returns the customer for the respective access token."""

    try:
        access_token = request.args['access_token']
    except KeyError:
        raise MissingAccessToken()

    try:
        access_token = AccessToken.get(AccessToken.token == access_token)
    except AccessToken.DoesNotExist:
        raise InvalidAccessToken()

    return access_token.customer


def _active_events():
    """Yields active events."""

    return Event.select().where(event_active())


def _get_events(customer):
    """Yields events of the querying customer."""

    for event in _active_events():
        if customer in event.customers:
            yield event


def _get_event(ident):
    """Returns the respective event of the querying customer."""

    try:
        event = Event.get(event_active() & (Event.id == ident))
    except Event.DoesNotExist:
        raise NoSuchEvent()

    if _get_customer() in event.customers:
        return event

    raise NoSuchEvent()


def _get_image(ident):
    """Returns the respective image."""

    try:
        event_image = Image.get(Image.id == ident)
    except Image.DoesNotExist:
        raise NoSuchImage()

    if _get_customer() in event_image.event.customers:
        return event_image

    raise NoSuchEvent()


def list_():
    """Lists the respective events."""

    return JSON([event.to_json() for event in _get_events(
        _get_customer())])


def get_event(ident):
    """Returns the respective event."""

    return JSON(_get_event(ident).to_json())


def get_image(ident):
    """Returns the respective image."""

    try:
        return Binary(_get_image(ident).watermarked)
    except OSError:     # Not an image.
        return Binary(_get_image(ident).data)


ROUTES = (
    ('GET', '/pub/event', list_, 'list_customer_events'),
    ('GET', '/pub/event/<int:ident>', get_event, 'get_customer_event'),
    ('GET', '/pub/image/<int:ident>', get_image, 'get_customer_image'))
