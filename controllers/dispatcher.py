#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import cherrypy
from sitebasis.models import Document, Site
from sitebasis.controllers.module import Module


class DispatcherModule(Module):

    def process_request(self, request):
        document, extra_path = self.resolve(request.path)
        request.document = document
        request.extra_path = extra_path
        self.validate(document)
        request.output = self.respond(request)

    def resolve(self, path):
        
        extra_path = []
        
        while path:
            document = Document.full_path.index.get("/".join(path))
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
            request.document.handler,
            request.extra_path
        )

        if handler is None:
            raise cherrypy.NotFound()

        return handler(*(request.extra_path or []), **cherrypy.request.params)

    def find_handler(self, handler, extra_path):
        
        is_default = False

        while handler and extra_path:

            child = getattr(handler, extra_path[0], None)

            if child:
                extra_path.pop(0)

                # Per-request controller instantiation
                if isinstance(child, type):
                    child = child()
                    child.parent = handler
            else:
                resolver = getattr(handler, "resolve", None)

                if resolver:
                    child = resolver(extra_path)
            
            if child is None:
                child = getattr(handler, "default", None)
                
                if child is not None:
                    is_default = True
                    handler = child
                    break

            handler = child

        while handler is not None and not callable(handler):
            handler = getattr(handler, "index", None)            
        
        if handler is not None and (
            (extra_path and not is_default)
            or not getattr(handler, "exposed", False)
        ):
            handler = None

        return handler

