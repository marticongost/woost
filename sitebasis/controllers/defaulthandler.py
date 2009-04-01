#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
from cocktail.modeling import cached_getter
from sitebasis.controllers import BaseCMSController


class DefaultHandler(BaseCMSController):
    """Default controller for published documents."""

    @cached_getter
    def document_template(self):
        template = self.context["document"].template

        if template is None:
            raise cherrypy.NotFound()

        return template

    @cached_getter
    def rendering_engine(self):
        engine_name = self.document_template.engine

        if engine_name:
            return self._get_rendering_engine(engine_name)
        else:
            return BaseCMSController.rendering_engine(self)

    @cached_getter
    def view_class(self):
        return self.document_template.identifier

