"""Event customer controller."""

from his import authenticated, authorized
from wsgilib import JSON

from hievents.orm import CustomerList

__all__ = ['ROUTES']


@authenticated
@authorized('hievents')
def list_():
    """Lists available customers."""

    return JSON([customer.to_dict() for customer in CustomerList])


ROUTES = (('GET', '/customers', list_, 'list_customers'),)
