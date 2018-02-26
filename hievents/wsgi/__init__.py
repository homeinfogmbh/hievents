"""WSGI application."""

from wsgilib import Application

from hinews.wsgi import article, customer, image, public, tag

APPLICATION = Application('hinews', debug=True, cors=True)
APPLICATION.add_routes(
    article.ROUTES + customer.ROUTES + image.ROUTES + public.ROUTES
    + tag.ROUTES)
