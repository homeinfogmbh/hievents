"""Event customer controller."""

from hinews.messages.customer import NoSuchCustomer, CustomerDeleted, \
    CustomerPatched
from his import DATA, authenticated, authorized
from wsgilib import JSON

from hievents.orm import CustomerList, EventCustomer

__all__ = ['ROUTES']


@authenticated
@authorized('hievents')
def list_():
    """Lists available customers."""

    return JSON([customer.to_dict() for customer in CustomerList])


@authenticated
@authorized('hievents')
def get(ident):
    """Returns the respective customer."""

    try:
        event_customer = EventCustomer.get(EventCustomer.id == ident)
    except EventCustomer.DoesNotExist:
        return NoSuchCustomer()

    return JSON(event_customer.to_dict())


@authenticated
@authorized('hievents')
def delete(ident):
    """Deletes the respective customer."""

    try:
        event_customer = EventCustomer.get(EventCustomer.id == ident)
    except EventCustomer.DoesNotExist:
        return NoSuchCustomer()

    event_customer.delete_instance()
    return CustomerDeleted()


@authenticated
@authorized('hievents')
def patch(ident):
    """Deletes the respective customer."""

    try:
        event_customer = EventCustomer.get(EventCustomer.id == ident)
    except EventCustomer.DoesNotExist:
        return NoSuchCustomer()

    event_customer.patch(DATA.json)
    event_customer.save()
    return CustomerPatched()


ROUTES = (
    ('GET', '/customer', list_, 'list_customers'),
    ('GET', '/customer/<int:ident>', get, 'get_customer'),
    ('DELETE', '/customer/<int:ident>', delete, 'delete_customer'),)
