#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
from sitebasis.controllers.application import Request


class DefaultHandler(object):

    @cherrypy.expose
    def index(self, *args, **kwargs):

        request = Request.current
        document = request.document
        template = document.template

        if template is None:
            raise cherrypy.NotFound()

        return request.cms.rendering.render(
            template.identifier,
            document = document
        )

