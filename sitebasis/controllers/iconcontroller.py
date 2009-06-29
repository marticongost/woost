#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2009
"""
import os

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import cherrypy
import Image
from pkg_resources import resource_filename
from cocktail.modeling import cached_getter
from cocktail.pkgutils import import_object
from sitebasis.models import Item
from sitebasis.models.thumbnails import ThumbnailParameterError
from sitebasis.controllers.basecmscontroller import BaseCMSController


class IconController(BaseCMSController):
    """A controller tasked with publishing icons and thumbnails for CMS items.
    """
    icon_format = "png"
    icon_size = 32

    @cherrypy.expose
    def __call__(self,
        id,
        width = None,
        height = None,
        format = None,
        icon_size = None,
        thumbnail = "true"):

        response_body = None
        item = self.get_item(id)

        # Try to produce a thumbnail for the requested item
        if not isinstance(item, type) and thumbnail == "true":
            response_body = self._serve_thumbnail(item, width, height, format)
        
        # If a thumbnail is not available, fall back to an icon
        if response_body is None:
            response_body = self._serve_icon(item, icon_size)
 
        # If neither a thumbnail or an icon are available, return a 404 HTTP
        # error
        if response_body is None:
            raise cherrypy.NotFound()
        
        return response_body

    def get_item(self, id):
        
        item = None

        if id:
            try:
                id = int(id)
            except:
                try:
                    item = import_object(id)
                except ImportError:
                    pass                    
            else:
                item = Item.get_instance(id)
                
                if item:
                    # Validate access
                    self.restrict_access(
                        action = "read",
                        target_instance = item
                    )
        
        if item is None:
            raise cherrypy.NotFound()
        
        return item

    @cached_getter
    def thumbnail_loader(self):
        """A thumbnail loader, used to produce thumbnails for requested items.
        @type: L{ThumbnailLoader<sitebasis.models.thumbnails.ThumbnailLoader>}
        """
        return self.context["cms"].thumbnail_loader

    @cached_getter
    def icon_resolver(self):
        """An icon resolver that will be used to choose a matching icon for
        items for which a thumbnail can't be generated.
        @type: str sequence
        """
        return self.context["cms"].icon_resolver

    def _serve_thumbnail(self, item, width, height, format):

        cms = self.context["cms"]
        thumbnail_loader = self.thumbnail_loader
        response_body = None

        # Thumbnail size
        if width is not None:
            width = int(width)

        if height is not None:
            height = int(height)
        
        # Thumbnail format
        if format is None:
            format = thumbnail_loader.default_format

        if format is not None and (width or height):

            # Try to obtain a thumbnail for the item
            try:
                image = thumbnail_loader.get_thumbnail(
                    item,
                    width,
                    height,
                    format = format
                )
            except ThumbnailParameterError:
                raise cherrypy.NotFound()
            
            if image:
                try:
                    mime_type = cms.image_format_mime_types[format]
                except KeyError:
                    pass
                else:
                    cherrypy.response.headers["Content-Type"] = mime_type

                buffer = StringIO()
                thumbnail_loader.save_thumbnail(image, buffer)
                response_body = buffer.getvalue()

        return response_body

    def _serve_icon(self, item, icon_size):
        
        response_body = None
        icon_resolver = self.icon_resolver
        icon_size = int(icon_size) if icon_size else self.icon_size
        icon_file = icon_resolver.find_icon(item, icon_size)

        if icon_file:
            response_body = cherrypy.lib.static.serve_file(                
                icon_file,
                content_type =
                    self.context["cms"].image_format_mime_types.get(
                        icon_resolver.icon_format    
                    )
            )

        return response_body

