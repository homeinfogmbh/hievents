"""WSGI application."""

from wsgilib import Application

from hievents.wsgi import customer, event, image, price, public, sub_event, tag

APPLICATION = Application('hievents', debug=True, cors=True)
APPLICATION.add_routes(
    event.ROUTES + customer.ROUTES + image.ROUTES + price.ROUTES
    + public.ROUTES + sub_event.ROUTES + tag.ROUTES)
