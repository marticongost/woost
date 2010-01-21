#-*- coding: utf-8 -*-
u"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
import cherrypy
from woost.controllers import BaseCMSController


class RedirectionController(BaseCMSController):

    def __call__(self):
        uri = self.context["publishable"].uri
        raise cherrypy.HTTPRedirect(uri)

