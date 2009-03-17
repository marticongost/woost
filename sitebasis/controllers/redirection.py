#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""

import cherrypy
from sitebasis.controllers import BaseCMSController


class Redirection(BaseCMSController):

    def __call__(self, *args, **kwargs):
        uri = self.context["document"].uri
        raise cherrypy.HTTPRedirect(uri)

