#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import cherrypy
from magicbullet.models import Publishable

class Dispatcher(object):

    def __init__(self, site):
        self.site = site

    def dispatch(self, path): 
        content, extra_path = self.resolve(path)        
        self.validate(content)
        return self.respond(content, extra_path)

    def resolve(self, path):
        
        base_path = path.split("/") if path else None
        extra_path = []
        
        while base_path:
            content = Publishable.path.index.get("/".join(base_path))
            if content:
                break
            else:
                extra_path.insert(0, base_path.pop())
        else:
            content = self.site.home
        
        return content, extra_path

    def validate(self, content):

        if content is None or not content.is_published():
            raise cherrypy.NotFound()
        
        self.site.restrict_access(
            action = "read",
            target_instance = content)

    def respond(self, content, extra_path = None):
        
        if extra_path is None:
            extra_path = []

        handler = self.get_content_handler(content, extra_path)
        
        if handler is None:
            raise cherrypy.NotFound()

        if getattr(handler, "im_self", None) is content:
            return handler(self.site, *extra_path)
        else:
            return handler(content, self.site, *extra_path)

    def get_content_handler(self, content, extra_path):
        
        handler = content.handler or content
        
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

