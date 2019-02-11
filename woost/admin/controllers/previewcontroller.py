#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import json
import cherrypy
from cocktail.persistence import InstanceNotFoundError
from cocktail.controllers import HTTPMethodController
from cocktail.translations import set_language
from cocktail.html import templates
from woost import app
from woost.models import (
    Item,
    PublishableObject,
    Website,
    Block,
    Slot,
    ModifyPermission
)
from woost.models.utils import get_matching_website
from woost.admin.dataimport import Import

JSON_MIME = "application/json"


class BasePreviewController(HTTPMethodController):

    data_import = Import

    @cherrypy.expose
    def GET(self, **kwargs):
        return self._preview()

    @cherrypy.expose
    def POST(self, **kwargs):
        return self._preview()

    def _preview(self):
        imp = self._import_data()
        self._setup_request(imp)
        return self._produce_content(imp)

    def _import_data(self):

        # Validate the content type
        content_type = cherrypy.request.headers["Content-Type"]
        if content_type != JSON_MIME:
            raise cherrypy.HTTPError(
                400,
                "POST data should be in %s format, received %s instead"
                % (JSON_MIME, content_type)
            )

        data = json.load(cherrypy.request.body)
        return self.data_import(
            data,
            dry_run = True
        )

    def _setup_request(self, imp):

        # Set the active publishable
        app.original_publishable = app.publishable

        if not isinstance(imp.obj, PublishableObject):
            raise cherrypy.HTTPError(400, "Invalid publishable: %r" % imp.obj)

        app.publishable = imp.obj

        # Set the active website
        website_identifier = cherrypy.request.params.pop("website", None)

        if website_identifier:
            website = Website.get_instance(identifier = website_identifier)
            if website is None and (
                app.publishable.websites
                and website not in app.publishable.websites
            ):
                raise cherrypy.HTTPError(
                    400,
                    "Invalid website: %s" % website_identifier
                )
            else:
                app.website = website
        else:
            app.website = get_matching_website(app.publishable)

        # Set the active language
        language = cherrypy.request.params.pop("language", None)
        if language:
            set_language(language)

        # Enable editing mode
        app.editing = True

    def _produce_content(self, imp):
        return ""

    def _require_param(self, param_name):
        try:
            return cherrypy.request.params[param_name]
        except KeyError:
            raise cherrypy.HTTPError(400, "Missing parameter %r" % param_name)

    def _resolve_object_param(self, param_name, imp, model = Item):

        id = self._require_param(param_name)

        obj = imp.get_instance(id, model)
        if obj is None:
            raise cherrypy.HTTPError(400, "Unknown object: %s" % id)

        return obj


class PagePreviewController(BasePreviewController):

    def _produce_content(self, imp):

        controller_class = app.publishable.resolve_controller()

        if not controller_class:
            raise cherrypy.NotFound()

        return controller_class()(**cherrypy.request.params)


class BlockPreviewController(BasePreviewController):

    def _produce_content(self, imp):
        block = self._resolve_object_param("block", imp, Block)
        # TODO: execute the block controller
        return block.create_view().render_page()


class StylesPreviewController(BasePreviewController):

    def _produce_content(self, imp):
        block = self._resolve_object_param("block", imp, Block)
        cherrypy.response.headers["Content-Type"] = "text/css; charset=utf-8"
        return block.get_embedded_css()


class SlotPreviewController(BasePreviewController):

    def _produce_content(self, imp):

        container = self._resolve_object_param("container", imp)
        slot = self._resolve_slot(imp, container.__class__)

        block_list = templates.new("woost.views.BlockList")
        block_list.container = container
        block_list.slot = slot
        return block_list.render_page()

    def _resolve_slot(self, imp, model):

        slot_name = self._require_param("slot")
        slot = model.get_member(slot_name)

        if slot is None or not isinstance(slot, Slot):
            raise cherrypy.HTTPError(400, "Unknown slot %r" % slot_name)

        return slot


class PreviewController(HTTPMethodController):
    page = PagePreviewController
    block = BlockPreviewController
    slot = SlotPreviewController
    styles = StylesPreviewController

