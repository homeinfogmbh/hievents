"""Price endpoints."""

from wsgilib import JSON

from hievents.messages.price import NoSuchPrice, PriceCreated, PriceDeleted, \
    PricePatched
from hievents.wsgi.event import get_event

__all__ = ['ROUTES']


def get_price(event, ident):
    """Returns the respective price."""

    try:
        return Price.get((price.event == event) & (price.id == ident))
    except Price.DoesNotExist:
        raise NoSuchPrice()


def list_(ident):
    """Lists prices of the respective event."""

    return JSON([price.to_dict() for price in get_event(ident).prices])


def get(event_id, price_id):
    """Returns the respective price."""

    return JSON(get_price(get_event(event_id), price_id).to_dict())


def post(ident):
    """Adds a price to the respective event."""

    event = get_event(ident)
    price = Price.from_dict(event, DATA.json)
    price.save()
    return PriceCreated(id=price.id)


def delete(event_id, price_id):
    """Deletes a price."""

    get_price(get_event(event_id), price_id).delete_instance()
    return PriceDeleted()


def patch(event_id, price_id):
    """Modiefies a price."""

    price = get_price(get_event(event_id), price_id)
    price.patch(DATA.json)
    price.save()
    return PricePatched()


ROUTES = (
    ('GET', '/event/<int:ident>/price', list_, 'list_prices'),
    ('GET', '/event/<int:event_id>/price/<int:price_id>', get, 'get_price'),
    ('POST', '/event/<int:ident>/price', post, 'add_sub_events'),
    ('DELETE', '/event/<int:event_id>/price/<int:price_id>', delete,
     'delete_price'),
    ('PATCH', '/event/<int:event_id>/price/<int:price_id>', patch,
     'patch_price'))
