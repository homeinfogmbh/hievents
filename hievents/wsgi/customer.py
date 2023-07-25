"""Event customer controller."""

from hinews.messages.customer import NoSuchCustomer, CustomerDeleted
from his import authenticated, authorized
from wsgilib import JSON

from hievents.orm import CustomerList, EventCustomer

__all__ = ["ROUTES"]


@authenticated
@authorized("hievents")
def list_():
    """Lists available customers."""

    return JSON([customer.to_json() for customer in CustomerList])


@authenticated
@authorized("hievents")
def get(ident):
    """Returns the respective customer."""

    try:
        event_customer = EventCustomer.get(EventCustomer.id == ident)
    except EventCustomer.DoesNotExist:
        return NoSuchCustomer()

    return JSON(event_customer.to_json())


@authenticated
@authorized("hievents")
def delete(ident):
    """Deletes the respective customer."""

    try:
        event_customer = EventCustomer.get(EventCustomer.id == ident)
    except EventCustomer.DoesNotExist:
        return NoSuchCustomer()

    event_customer.delete_instance()
    return CustomerDeleted()


ROUTES = (
    ("GET", "/customer", list_, "list_customers"),
    ("GET", "/customer/<int:ident>", get, "get_customer"),
    ("DELETE", "/customer/<int:ident>", delete, "delete_customer"),
)
