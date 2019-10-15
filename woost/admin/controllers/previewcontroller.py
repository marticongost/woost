"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Any, Type

import cherrypy
from cocktail.modeling import GenericMethod
from cocktail.controllers import HTTPMethodController, read_json
from cocktail.translations import set_language
from cocktail.html import templates

from woost import app
from woost.models import (
    Item,
    PublishableObject,
    Website,
    Block,
    BlocksCatalog,
    Slot
)
from woost.models.utils import get_matching_website
from woost.admin.dataimport import Import

get_blocks_preview_target = GenericMethod("get_blocks_preview_target")

@get_blocks_preview_target.implementation_for(PublishableObject)
def get_publishable_blocks_preview_target(self):
    return self

@get_blocks_preview_target.implementation_for(BlocksCatalog)
def get_blocks_catalog_blocks_preview_target(self):
    website = app.website or Website.select()[0]
    return website and website.home


class BasePreviewController(HTTPMethodController):

    data_import: Type[Import] = Import

    @cherrypy.expose
    def GET(self, **kwargs):
        return self._preview()

    @cherrypy.expose
    def POST(self, **kwargs):
        return self._preview()

    def _preview(self) -> str:
        imp = self._import_data()
        self._setup_request(imp)
        return self._produce_content(imp)

    def _import_data(self):
        data = read_json()
        return self.data_import(
            data,
            user = app.user,
            dry_run = True
        )

    def _setup_request(self, imp: Import):

        # Set the active publishable
        app.publishable = self._resolve_preview_target(imp)

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

    def _produce_content(self, imp: Import) -> str:
        return ""

    def _require_param(self, param_name: str) -> Any:
        try:
            return cherrypy.request.params[param_name]
        except KeyError:
            raise cherrypy.HTTPError(400, "Missing parameter %r" % param_name)

    def _resolve_preview_target(self, imp: Import) -> PublishableObject:

        publishable = get_blocks_preview_target(imp.obj)

        if not isinstance(publishable, PublishableObject):
            raise cherrypy.HTTPError(
                400,
                "Invalid publishable source: %r" % imp.obj
            )

        return publishable

    def _resolve_object_param(
            self,
            param_name: str,
            imp: Import,
            model: Type[Item] = Item) -> Item:

        id = self._require_param(param_name)

        try:
            id = int(id)
        except ValueError:
            raise cherrypy.HTTPError(
                400,
                "Invalid object id, expected an integer: %s" % id
            )

        obj = imp.get_instance(id, model)
        if obj is None:
            raise cherrypy.HTTPError(400, "Unknown object: %s" % id)

        return obj


class PagePreviewController(BasePreviewController):

    def _produce_content(self, imp: Import) -> str:

        controller_class = app.publishable.resolve_controller()

        if not controller_class:
            raise cherrypy.NotFound()

        return controller_class()(**cherrypy.request.params)


class BlockPreviewController(BasePreviewController):

    def _produce_content(self, imp: Import) -> str:

        block = self._resolve_object_param("block", imp, Block)

        if block.is_published():
            view = block.create_view()
            if view:
                return view.render_page()

        return ""


class StylesPreviewController(BasePreviewController):

    def _produce_content(self, imp: Import) -> str:
        block = self._resolve_object_param("block", imp, Block)
        cherrypy.response.headers["Content-Type"] = "text/css; charset=utf-8"
        return block.get_embedded_css()


class SlotPreviewController(BasePreviewController):

    def _produce_content(self, imp: Import) -> str:

        container = self._resolve_object_param("container", imp)
        slot = self._resolve_slot(imp, container.__class__)

        block_list = templates.new(slot.view_class)
        block_list.container = container
        block_list.slot = slot
        return block_list.render_page()

    def _resolve_slot(self, imp: Import, model: Type[Item]) -> Slot:

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

