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

