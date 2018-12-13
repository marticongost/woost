#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
import os
import cherrypy
import re
from cocktail.controllers import (
    serve_file,
    resolve_object_ref,
    redirect
)
from woost import app
from woost.models import Item, File, RenderPermission
from woost.models.rendering import (
    require_rendering,
    ImageFactory,
    BadRenderingRequest
)
from woost.models.rendering.formats import formats_by_extension
from woost.controllers.basecmscontroller import BaseCMSController

generic_image_factory_pattern = re.compile(r"^factory(\d+)$")


class ImagesController(BaseCMSController):
    """A controller that produces, caches and serves images representing the
    different kinds of content managed by the CMS.
    """

    def __call__(self, id, processing, *args, **kwargs):

        # Get the requested element; either an object in the database or an
        # upload that hasn't been comitted yet
        item = None

        UPLOAD_PREFIX = "upload-"
        if id.startswith(UPLOAD_PREFIX):
            upload_id = id[len(UPLOAD_PREFIX):]
            upload = app.async_uploader.get(upload_id)
            if upload:
                item = File()
                item._v_upload_id = upload_id
                item.file_name = upload.name
                item.file_size = upload.size
                item.mime_type = upload.type
        else:
            item = resolve_object_ref(Item, id)

        # Make sure the selected element exists
        if item is None:
            raise cherrypy.NotFound()

        # Normalize the URL to use a local id
        if id == item.global_id:
            redirect(
                cherrypy.url().replace("/" + id + "/", "/%d/" % item.id)
            )

        # Parse the given processing string, splitting the image factory from
        # the image format (ie. "home_thumbnail.png" -> ("home_thumbnail", "PNG"))
        parts = processing.rsplit(".", 1)
        parameters = None

        if len(parts) == 2:
            factory_id, ext = parts
            format = formats_by_extension.get(ext)
            if format is None:
                raise cherrypy.HTTPError(
                    400,
                    "Invalid image extension: %s" % ext
                )
        else:
            factory_id = processing
            format = None

        factory = ImageFactory.get_instance(identifier = factory_id)

        if factory is None:
            match = generic_image_factory_pattern.match(factory_id)
            if match:
                try:
                    factory_id = int(match.group(1))
                    factory = ImageFactory.require_instance(factory_id)
                except:
                    pass

            if factory is None:
                raise cherrypy.HTTPError(
                    400,
                    "Invalid image factory id: %s" % factory_id
                )

        # Deny access to unauthorized elements
        app.user.require_permission(
            RenderPermission,
            target = item,
            image_factory = factory
        )

        try:
            image_cache_file = require_rendering(
                item,
                factory,
                format,
                parameters
            )
        except BadRenderingRequest, ex:
            raise cherrypy.HTTPError(400, ex.message)

        return serve_file(image_cache_file)

