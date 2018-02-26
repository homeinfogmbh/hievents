"""Public customer interface without
HIS authentication or authorization.
"""
from flask import request

from wsgilib import JSON, XML, Binary

from hinews import dom
from hinews.messages.article import NoSuchArticle
from hinews.messages.image import NoSuchImage
from hinews.messages.public import MissingAccessToken, InvalidAccessToken
from hinews.orm import article_active, Article, ArticleImage, AccessToken

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


def _active_articles():
    """Yields active articles."""

    return Article.select().where(article_active())


def _get_articles(customer):
    """Yields articles of the querying customer."""

    for article in _active_articles():
        if customer in article.customers:
            yield article


def _get_article(ident):
    """Yields articles of the querying customer."""

    try:
        article = Article.get(article_active() & (Article.id == ident))
    except Article.DoesNotExist:
        raise NoSuchArticle()

    if _get_customer() in article.customers:
        return article

    raise NoSuchArticle()


def _get_image(ident):
    """Returns the respective image."""

    try:
        article_image = ArticleImage.get(ArticleImage.id == ident)
    except ArticleImage.DoesNotExist:
        raise NoSuchImage()

    if _get_customer() in article_image.article.customers:
        return article_image

    raise NoSuchArticle()


def list_():
    """Lists the respective news."""

    try:
        request.args['xml']
    except KeyError:
        return JSON([article.to_dict() for article in _get_articles(
            _get_customer())])

    news = dom.news()
    news.article = [article.to_dom() for article in _get_articles(
        _get_customer())]
    return XML(news)


def get_article(ident):
    """Returns the respective article."""

    return JSON(_get_article(ident).to_dict())


def get_image(ident):
    """Returns the respective image."""

    try:
        return Binary(_get_image(ident).watermarked)
    except OSError:     # Not an image.
        return Binary(_get_image(ident).data)


ROUTES = (
    ('GET', '/pub/article', list_, 'list_customer_articles'),
    ('GET', '/pub/article/<int:ident>', get_article, 'get_customer_article'),
    ('GET', '/pub/image/<int:ident>', get_image, 'get_customer_image'))
