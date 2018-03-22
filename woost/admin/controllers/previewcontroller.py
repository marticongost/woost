#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.persistence import InstanceNotFoundError
from cocktail.controllers import HTTPMethodController
from cocktail.translations import set_language
from woost import app
from woost.models import get_publishable, Website, ModifyPermission
from woost.models.utils import get_matching_website


class PreviewController(HTTPMethodController):

    @cherrypy.expose
    def GET(self, publishable, **kwargs):
        return self._preview(publishable = publishable, **kwargs)

    @cherrypy.expose
    def POST(self, **kwargs):
        return self._preview(publishable = publishable, **kwargs)

    def _preview(
        self,
        publishable,
        language = None,
        website = None,
        **kwargs
    ):
        try:
            id = int(publishable)
        except ValueError:
            raise cherrypy.HTTPError(400, "Non numeric publishable ID")

        try:
            app.publishable = get_publishable(id)
        except InstanceNotFoundError:
            raise cherrypy.HTTPError(400, "Invalid publishable: %d" % id)

        if website:
            website_obj = Website.get_instance(identifier = website)
            if website_obj is None and (
                app.publishable.websites
                and website_obj not in app.publishable.websites
            ):
                raise cherrypy.HTTPError(400, "Invalid website: %s" % website)
            else:
                app.website = website_obj
        else:
            app.website = get_matching_website(app.publishable)

        if language:
            set_language(language)

        app.user.require_permission(
            ModifyPermission,
            target = app.publishable
        )

        app.editing = True

        controller_class = app.publishable.resolve_controller()

        if not controller_class:
            raise cherrypy.NotFound()

        return controller_class()(**kwargs)

