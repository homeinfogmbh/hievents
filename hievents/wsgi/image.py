"""Event image handlers."""

from flask import request

from hinews.messages.image import NoSuchImage, ImageDeleted, ImagePatched
from his import authenticated, authorized
from wsgilib import Binary, JSON

from hievents.orm import Image

__all__ = ["ROUTES"]


def get_image(ident):
    """Returns the respective image."""

    try:
        return Image.get(Image.id == ident)
    except Image.DoesNotExist:
        raise NoSuchImage()


@authenticated
@authorized("hievents")
def list_all():
    """Lists all available images."""

    return JSON([image.to_json() for image in Image])


@authenticated
@authorized("hievents")
def get(ident):
    """Returns a specific image."""

    return Binary(get_image(ident).data)


@authenticated
@authorized("hievents")
def delete(ident):
    """Deletes the respective image."""

    get_image(ident).delete_instance()
    return ImageDeleted()


@authenticated
@authorized("hievents")
def patch(ident):
    """Modifies image meta data."""

    image = get_image(ident)
    image.patch_json(request.json)
    image.save()
    return ImagePatched()


ROUTES = (
    ("GET", "/image", list_all, "list_images"),
    ("GET", "/image/<int:ident>", get, "get_image"),
    ("DELETE", "/image/<int:ident>", delete, "delete_image"),
    ("PATCH", "/image/<int:ident>", patch, "patch_image"),
)
