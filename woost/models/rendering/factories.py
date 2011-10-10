#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import OrderedDict
from woost.models.rendering.contentrenderersregistry import (
    content_renderers,
    icon_renderers
)

image_factories = OrderedDict()

def image_factory(func):
    """A decorator used to register image factories."""
    image_factories[func.func_name] = func
    return func

@image_factory
def default(item):
    """An image factory that returns the full size, unprocessed image for the
    item.
    """
    return content_renderers.render(item)

@image_factory
def icon16(item):
    """An image factory that returns the item's 16x16 icon."""
    return icon_renderers.render(item, size = 16)

@image_factory
def icon32(item):
    """An image factory that returns the item's 32x32 icon."""
    return icon_renderers.render(item, size = 32)

@image_factory
def backoffice_thumbnail(item):
    """Content preview or icon for thumbnails in the back office."""
    image = None
    if not isinstance(item, type):
        image = content_renderers.render(
            item, effects = "thumbnail(100,100)/frame(1,'ddd',4,'eee')"
        )
    return image or icon_renderers.render(item, size = 32)

@image_factory
def backoffice_small_thumbnail(item):
    """Smaller content preview or icon for thumbnails in the back office."""
    image = None
    if not isinstance(item, type):
        image = content_renderers.render(
            item, effects = "thumbnail(32,32)"
        )
    return image or icon_renderers.render(item, size = 16)

@image_factory
def image_gallery_close_up(item):
    """Image factory for the close up views in the `woost.views.ImageGallery`
    control.
    """
    return content_renderers.render(item, effects = "fit(900,700)")

@image_factory
def image_gallery_thumbnail(item):
    """Image factory for the thumbnails in the `woost.views.ImageGallery`
    control.
    """
    return content_renderers.render(item, effects = "fit(200,150)")

