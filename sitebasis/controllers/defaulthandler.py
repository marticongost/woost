#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
from cocktail.controllers import request_property
from sitebasis.models import Document
from sitebasis.controllers import BaseCMSController


class DefaultHandler(BaseCMSController):
    """Default controller for published documents."""

    @request_property
    def document_template(self):
        template = cherrypy.request.document.template

        if template is None:
            raise cherrypy.NotFound()

        return template

    @request_property
    def rendering_engine(self):
        engine_name = self.document_template.engine

        if engine_name:
            return self._get_rendering_engine(engine_name)
        else:
            return BaseCMSController.rendering_engine(self)

    @request_property
    def view_class(self):
        return self.document_template.identifier


# Set as the default document handler
Document.handler = DefaultHandler()

