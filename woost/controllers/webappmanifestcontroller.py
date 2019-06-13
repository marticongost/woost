"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from copy import deepcopy
import json

import cherrypy
from cocktail.controllers import Cached, Controller, request_property
from cocktail.controllers.imageupload import get_image_size

from woost import app
from woost.models import Configuration


class WebAppManifestController(Cached, Controller):
    """A controller that generates a web app manifest.

    https://developer.mozilla.org/en-US/docs/Web/Manifest
    """

    defaults = {
        "start_url": "/",
        "display": "standalone"
    }

    @request_property
    def invalidation(self):
        invalidation = Cached.invalidation(self)
        invalidation.depends_on(app.website)
        invalidation.depends_on(app.website.icons)
        return invalidation

    def _produce_content(self, **kwargs):
        cherrypy.response.headers["Content-Type"] = "application/manifest+json"
        return json.dumps(self.get_manifest()).encode("utf-8")

    def get_manifest(self):
        data = deepcopy(self.defaults)
        data["name"] = app.website.site_name
        data["icons"] = icons = []
        for icon in Configuration.instance.get_setting("icons"):
            icon_data = self.export_icon(icon)
            if icon_data:
                icons.append(icon_data)
        return data

    def export_icon(self, icon):
        try:
            size = get_image_size(icon.file_path)
        except:
            return None
        else:
            return {
                "src": icon.get_uri(),
                "type": icon.mime_type,
                "sizes": "%dx%d" % size
            }

