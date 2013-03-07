#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
import cherrypy
from woost.controllers import BaseCMSController


class IssuuDocumentController(BaseCMSController):

    def __call__(self, *args, **kwargs):
        uri = self.context["publishable"].issuu_document_url
        raise cherrypy.HTTPRedirect(uri)


