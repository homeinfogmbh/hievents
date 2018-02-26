"""Article image handlers."""

from his import ACCOUNT, DATA, authenticated, authorized
from his.messages import MissingData, InvalidData
from wsgilib import Binary, JSON

from hinews.messages.image import NoSuchImage, NoImageProvided, \
    NoMetaDataProvided, ImageAdded, ImageDeleted, ImagePatched
from hinews.orm import ArticleImage
from hinews.wsgi.article import get_article

__all__ = ['ROUTES']


def get_image(ident):
    """Returns the respective image."""

    try:
        return ArticleImage.get(ArticleImage.id == ident)
    except ArticleImage.DoesNotExist:
        raise NoSuchImage()


@authenticated
@authorized('hinews')
def list_():
    """Lists all available articles."""

    return JSON([image.to_dict() for image in ArticleImage])


@authenticated
@authorized('hinews')
def list_article_images(ident):
    """Lists all available articles."""

    return JSON([image.to_dict() for image in get_article(ident).images])


@authenticated
@authorized('hinews')
def get(ident):
    """Returns a specific article."""

    return Binary(get_image(ident).data)


@authenticated
@authorized('hinews')
def post(ident):
    """Adds a new article."""

    files = DATA.files

    try:
        image = files['image']
    except KeyError:
        raise NoImageProvided()

    try:
        metadata = files['metadata']
    except KeyError:
        raise NoMetaDataProvided()

    try:
        image = get_article(ident).images.add(
            image.bytes, metadata.json, ACCOUNT)
    except KeyError as key_error:
        raise MissingData(key=key_error.args[0])
    except ValueError as value_error:
        raise InvalidData(hint=value_error.args[0])

    return ImageAdded(id=image.id)


@authenticated
@authorized('hinews')
def delete(ident):
    """Adds a new article."""

    get_image(ident).delete_instance()
    return ImageDeleted()


@authenticated
@authorized('hinews')
def patch(ident):
    """Adds a new article."""

    image = get_image(ident)
    image.patch(DATA.json)
    image.save()
    return ImagePatched()


ROUTES = (
    ('GET', '/article/<int:ident>/images', list_article_images,
     'list_article_images'),
    ('POST', '/article/<int:ident>/images', post, 'post_article_image'),
    ('GET', '/image', list_, 'list_images'),
    ('GET', '/image/<int:ident>', get, 'get_image'),
    ('DELETE', '/image/<int:ident>', delete, 'delete_image'),
    ('PATCH', '/image/<int:ident>', patch, 'patch_image'))
