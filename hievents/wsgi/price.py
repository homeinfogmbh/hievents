"""Price endpoints."""

from flask import request

from wsgilib import JSON

from hievents.messages.price import NoSuchPrice, PriceDeleted, PricePatched
from hievents.orm import Price

__all__ = ['ROUTES']


def list_():
    """Lists prices of the respective event."""

    return JSON([price.to_json() for price in Price])


def get(ident):
    """Returns the respective price."""

    try:
        price = Price.get(Price.id == ident)
    except Price.DoesNotExist:
        raise NoSuchPrice()

    return JSON(price.to_json())


def delete(ident):
    """Deletes a price."""

    try:
        price = Price.get(Price.id == ident)
    except Price.DoesNotExist:
        raise NoSuchPrice()

    price.delete_instance()
    return PriceDeleted()


def patch(ident):
    """Modiefies a price."""

    try:
        price = Price.get(Price.id == ident)
    except Price.DoesNotExist:
        raise NoSuchPrice()

    price.patch_json(request.json)
    return PricePatched()


ROUTES = (
    ('GET', '/price/<int:ident>/price', list_, 'list_prices'),
    ('GET', '/price/<int:ident>', get, 'get_price'),
    ('DELETE', '/price/<int:ident>', delete, 'delete_price'),
    ('PATCH', '/price/<int:ident>', patch, 'patch_price'))
