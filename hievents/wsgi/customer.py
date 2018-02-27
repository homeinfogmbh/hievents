"""Event customer controller."""

from hinews.messages.customer import NoSuchCustomer, CustomerAdded, \
    CustomerDeleted
from his import DATA, authenticated, authorized
from homeinfo.crm import Customer
from wsgilib import JSON

from hievents.orm import InvalidCustomer, CustomerList
from hievents.wsgi.event import get_event

__all__ = ['ROUTES']


def get_customer(cid):
    """Returns the respective customer."""

    try:
        return Customer.get(Customer.id == cid)
    except Customer.DoesNotExist:
        raise NoSuchCustomer()


@authenticated
@authorized('hievents')
def list_():
    """Lists available customers."""

    return JSON([customer.to_dict() for customer in CustomerList])


@authenticated
@authorized('hievents')
def get(ident):
    """Lists customer of the respective event."""

    return JSON([
        customer.to_dict() for customer in get_event(ident).customers])


@authenticated
@authorized('hievents')
def post(ident):
    """Adds a customer to the respective event."""

    try:
        get_event(ident).customers.add(get_customer(DATA.text))
    except InvalidCustomer:
        return NoSuchCustomer()

    return CustomerAdded()


@authenticated
@authorized('hievents')
def delete(event_id, customer_id):
    """Deletes the respective customer from the event."""

    get_event(event_id).customers.delete(get_customer(customer_id))
    return CustomerDeleted()


ROUTES = (
    ('GET', '/customers', list_, 'list_customers'),
    ('GET', '/event/<int:ident>/customers', get, 'get_event_customers'),
    ('POST', '/event/<int:ident>/customers', post, 'post_event_customer'),
    ('DELETE', '/event/<int:event_id>/customers/<customer_id>', delete,
     'delete_event_customer'))
