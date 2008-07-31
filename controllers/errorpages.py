#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import cherrypy
from magicbullet.models import Site, AccessDeniedError
from magicbullet.controllers.module import Module
from magicbullet.controllers.authentication import AuthenticationFailedError


class ErrorPages(Module):

    def handle_error(self, request, error, handled):

        site = Site.main
        error_page = None

        if isinstance(error, cherrypy.NotFound):
            status = 404
            error_page = site.not_found_error_page
        
        elif isinstance(error, (AccessDeniedError, AuthenticationFailedError)):
            status = 403
            error_page = site.forbidden_error_page
       
        if error_page is None:
            status = 500
            error_page = site.generic_error_page

        if error_page:
            dispatcher = self.application.dispatcher
            dispatcher.validate(error_page)            
            request.publishable = error_page
            request.extra_path = None            
            cherrypy.request.status = 404 
            request.output = dispatcher.respond(request)
            return True

