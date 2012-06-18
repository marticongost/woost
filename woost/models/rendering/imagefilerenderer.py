#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
from woost.models.file import File
from woost.models.rendering.renderer import Renderer
from woost.models.rendering.formats import formats_by_mime_type


class ImageFileRenderer(Renderer):
    """A content renderer that handles image files."""

    instantiable = True

    def can_render(self, item, **parameters):
        return (
            isinstance(item, File)
            and item.resource_type == "image"
            and item.mime_type in formats_by_mime_type
        )

    def render(self, item, **parameters):
        return item.file_path

    def last_change_in_appearence(self, item):
        return max(
            os.stat(item.file_path).st_mtime,
            Renderer.last_change_in_appearence(self, item)
        )

