#-*- coding: utf-8 -*-
'''

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
'''
from woost.models.rendering import image_factory, content_renderers

@image_factory
def edit_blocks_thumbnail(item):
    """Content preview or icon for thumbnails in the back office."""
    return content_renderers.render(
        item, effects = "thumbnail(75,75)/frame(1,'ccc',4,'eee')"
    )

