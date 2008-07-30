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
        
        handler = self.get_content_handler(content)

        if getattr(handler, "accepts_extra_path", False):

            if extra_path is None:
                extra_path = []

            return handler(content, extra_path)
        else:
            if extra_path:
                raise cherrypy.NotFound()

            return handler(content)

    def get_content_handler(self, content):
        return content.handler \
            or getattr(content.__class__, "handle_request", None) \
            or self.default_handler

    def get_content_template(self, content):
        return content.template

    def render_content(self, content):

        template = self.get_content_template(content)

        if template is None:
            raise cherrypy.NotFound()

        return self.site.render(template.identifier, item = content)
    
    default_handler = render_content

