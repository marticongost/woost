#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import cherrypy
from sitebasis.models import Document, Site
from sitebasis.models.document import exposed
from sitebasis.controllers.module import Module


class Dispatcher(Module):

    def process_request(self, request):
        
        document, extra_path = self.resolve(request.path)
        request.document = document
        request.extra_path = extra_path
        
        self.validate(document)

        request.output = self.respond(request)

    def resolve(self, path):
        
        extra_path = []
        
        while path:
            document = Document.path.index.get("/".join(path))
            if document:
                break
            else:
                extra_path.insert(0, path.pop())
        else:
            document = Site.main.home
        
        return document, extra_path

    def validate(self, document):

        if document is None or not document.is_published():
            raise cherrypy.NotFound()
        
        self.application.authorization.restrict_access(
            action = "read",
            target_instance = document)

    def respond(self, request):
        
        handler = self.find_handler(
            request.document.handler or request.document,
            request.extra_path)
        
        if handler is None:
            raise cherrypy.NotFound()

        return handler(self.application, request)

    def find_handler(self, handler, extra_path):
        
        while extra_path:

            resolver = getattr(handler, "resolve", None)

            if resolver:
                child = resolver(extra_path)
            else:
                child = getattr(handler, extra_path[0], None)
                if child:
                    extra_path.pop(0)
            
            if child is None:
                child = getattr(handler, "default", None)
                break

            handler = child
        
        while handler is not None and not callable(handler):
            handler = getattr(handler, "index", None)            
        
        if handler is not None and not getattr(handler, "exposed", False):
            handler = None

        return handler


class Resolver(object):

    def __init__(self, function):
        self.function = function

    def resolve(self, cms, request):
        return self.function(self, cms, request)

resolver = Resolver

