"""Event image handlers."""

from hinews.messages.image import NoSuchImage, NoImageProvided, \
    NoMetaDataProvided, ImageAdded, ImageDeleted, ImagePatched
from his import ACCOUNT, DATA, authenticated, authorized
from his.messages import MissingData, InvalidData
from wsgilib import Binary, JSON

from hievents.orm import EventImage
from hievents.wsgi.event import get_event

__all__ = ['ROUTES']


def get_image(ident):
    """Returns the respective image."""

    try:
        return EventImage.get(EventImage.id == ident)
    except EventImage.DoesNotExist:
        raise NoSuchImage()


@authenticated
@authorized('hievents')
def list_():
    """Lists all available images."""

    return JSON([image.to_dict() for image in EventImage])


@authenticated
@authorized('hievents')
def list_event_images(ident):
    """Lists all images of the respective event."""

    return JSON([image.to_dict() for image in get_event(ident).images])


@authenticated
@authorized('hievents')
def get(ident):
    """Returns a specific image."""

    return Binary(get_image(ident).data)


@authenticated
@authorized('hievents')
def post(ident):
    """Adds a new image to the respective event."""

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
        image = get_event(ident).images.add(
            image.bytes, metadata.json, ACCOUNT)
    except KeyError as key_error:
        raise MissingData(key=key_error.args[0])
    except ValueError as value_error:
        raise InvalidData(hint=value_error.args[0])

    return ImageAdded(id=image.id)


@authenticated
@authorized('hievents')
def delete(ident):
    """Deletes the respective image."""

    get_image(ident).delete_instance()
    return ImageDeleted()


@authenticated
@authorized('hievents')
def patch(ident):
    """Modifies image meta data."""

    image = get_image(ident)
    image.patch(DATA.json)
    image.save()
    return ImagePatched()


ROUTES = (
    ('GET', '/event/<int:ident>/images', list_event_images,
     'list_event_images'),
    ('POST', '/event/<int:ident>/images', post, 'post_event_image'),
    ('GET', '/image', list_, 'list_images'),
    ('GET', '/image/<int:ident>', get, 'get_image'),
    ('DELETE', '/image/<int:ident>', delete, 'delete_image'),
    ('PATCH', '/image/<int:ident>', patch, 'patch_image'))
