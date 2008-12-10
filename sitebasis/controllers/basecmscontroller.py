#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
import cherrypy
from cocktail.persistence import datastore
from cocktail.controllers import Controller
from sitebasis.models import Site


class BaseCMSController(Controller):

    def _render_template(self):

        # Pass the request context to the template
        request = cherrypy.request
        cms = request.cms
        
        self.output.update(
            cms = cms,
            site = Site.main,
            user = cms.authentication.user,
            document = request.document
        )

        return Controller._render_template(self)

    def document_uri(self, *args):
        request = cherrypy.request
        return request.cms.uri(request.document.fullpath, *args)

    @classmethod
    def handle_after_request(cls, event):
        # Drop any uncommitted change
        datastore.abort()
        datastore.close()

