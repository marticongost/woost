#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import json
import cherrypy
from cocktail.persistence import InstanceNotFoundError
from cocktail.controllers import HTTPMethodController
from cocktail.translations import set_language
from woost import app
from woost.models import get_publishable, Website, Block, ModifyPermission
from woost.models.utils import get_matching_website
from woost.admin.models.dataimport import Import


def setup_preview_request(publishable, kwargs):

    try:
        id = int(publishable)
    except ValueError:
        raise cherrypy.HTTPError(400, "Non numeric publishable ID")

    app.original_publishable = app.publishable

    try:
        app.publishable = get_publishable(id)
    except InstanceNotFoundError:
        raise cherrypy.HTTPError(400, "Invalid publishable: %d" % id)

    website_identifier = kwargs.pop("website", None)

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

    language = kwargs.pop("language", None)
    if language:
        set_language(language)

    app.user.require_permission(
        ModifyPermission,
        target = app.publishable
    )

    app.editing = True


class PagePreviewController(HTTPMethodController):

    data_import = Import

    @cherrypy.expose
    def GET(self, publishable, **kwargs):
        return self._preview(publishable = publishable, **kwargs)

    @cherrypy.expose
    def POST(self, publishable, **kwargs):
        return self._preview(publishable = publishable, **kwargs)

    def _preview(
        self,
        publishable,
        **kwargs
    ):
        setup_preview_request(publishable, kwargs)
        self._load_page_data(app.publishable)
        controller_class = app.publishable.resolve_controller()

        if not controller_class:
            raise cherrypy.NotFound()

        return controller_class()(**kwargs)

    def _load_page_data(self, publishable):
        if (
            cherrypy.request.method == "POST"
            and int(cherrypy.request.headers["Content-Length"])
        ):
            # Validate the content type
            content_type = cherrypy.request.headers["Content-Type"]
            JSON_MIME = "application/json"
            if content_type != JSON_MIME:
                raise cherrypy.HTTPError(
                    400,
                    "POST data should be in %s format, received %s instead"
                    % (JSON_MIME, content_type)
                )

            data = json.load(cherrypy.request.body)
            self.data_import(publishable, data)


class BaseBlockPreviewController(HTTPMethodController):

    data_import = Import

    @cherrypy.expose
    def GET(self, publishable, block, **kwargs):
        return self._preview(publishable = publishable, block_id = block, **kwargs)

    @cherrypy.expose
    def POST(self, publishable, block, **kwargs):
        return self._preview(publishable = publishable, block_id = block, **kwargs)

    def _preview(self, publishable, block_id, **kwargs):
        setup_preview_request(publishable, kwargs)
        block = self._get_block(block_id)
        self._load_block_data(block)
        return self._produce_block_content(block)

    def _get_block(self, block_id):

        try:
            block_id = int(block_id)
        except ValueError:
            raise cherrypy.HTTPError(400, "Non numeric block ID")

        block = Block.get_instance(block_id)
        if block is None:
            raise cherrypy.HTTPError(400, "Invalid block: %s" % block_id)

        return block

    def _load_block_data(self, block):
        if (
            cherrypy.request.method == "POST"
            and int(cherrypy.request.headers["Content-Length"])
        ):
            # Validate the content type
            content_type = cherrypy.request.headers["Content-Type"]
            JSON_MIME = "application/json"
            if content_type != JSON_MIME:
                raise cherrypy.HTTPError(
                    400,
                    "POST data should be in %s format, received %s instead"
                    % (JSON_MIME, content_type)
                )

            data = json.load(cherrypy.request.body)
            self.data_import(block, data)

    def _produce_block_content(self):
        raise ValueError(
            "%s hasn't implemented the _produce_block_content() method"
            % self.__class__.__name__
        )


class BlockPreviewController(BaseBlockPreviewController):

    def _produce_block_content(self, block):
        # TODO: execute the block controller
        return block.create_view().render_page()


class StylesImport(Import):

    def should_import_member(self, obj, member):
        return member in (
            Block.embedded_styles,
            Block.embedded_styles_initialization
        )


class StylesPreviewController(BaseBlockPreviewController):

    data_import = StylesImport

    def _produce_block_content(self, block):
        cherrypy.response.headers["Content-Type"] = "text/css; charset=utf-8"
        return block.get_embedded_css()


class PreviewController(HTTPMethodController):
    page = PagePreviewController
    block = BlockPreviewController
    styles = StylesPreviewController

