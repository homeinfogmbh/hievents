"""WSGI application."""

from wsgilib import Application

from hievents.wsgi import customer, event, image, public, tag

APPLICATION = Application('hievents', debug=True, cors=True)
APPLICATION.add_routes(
    article.ROUTES + customer.ROUTES + image.ROUTES + public.ROUTES
    + tag.ROUTES)
