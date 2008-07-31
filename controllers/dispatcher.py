#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import cherrypy
from magicbullet.models import Publishable, Site
from magicbullet.controllers.module import Module


class Dispatcher(Module):

    def process_request(self, request):
        
        publishable, extra_path = self.resolve(request.path)
        request.publishable = publishable
        request.extra_path = extra_path
        
        self.validate(publishable)

        request.output = self.respond(request)

    def resolve(self, path):
        
        extra_path = []
        
        while path:
            publishable = Publishable.path.index.get("/".join(path))
            if publishable:
                break
            else:
                extra_path.insert(0, path.pop())
        else:
            publishable = Site.main.home
        
        return publishable, extra_path

    def validate(self, publishable):

        if publishable is None or not publishable.is_published():
            raise cherrypy.NotFound()
        
        self.application.authorization.restrict_access(
            action = "read",
            target_instance = publishable)

    def respond(self, request):
        
        handler = self.find_handler(request.publishable, request.extra_path)
        
        if handler is None:
            raise cherrypy.NotFound()

        return handler(self.application, request)

    def find_handler(self, publishable, extra_path):
        
        handler = publishable.handler or publishable
        
        while extra_path:
            child = getattr(handler, extra_path[0], None)
            
            if child is None:
                handler = getattr(handler, "default", None)
                break

            handler = child
            extra_path.pop(0)
        
        if handler is not None and not callable(handler):
            handler = getattr(handler, "index", None)
        
        if handler is not None and not getattr(handler, "exposed", False):
            handler = None

        return handler

