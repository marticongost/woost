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
        content = self.resolve(path)
        self.validate(content)
        return self.respond(content)

    def resolve(self, path):
        if path:
            return Publishable.path.index.get(path)
        else:
            return self.site.home

    def validate(self, content):

        if content is None or not content.is_published():
            raise cherrypy.NotFound()
        
        self.site.restrict_access(
            action = "read",
            target_instance = content)

    def respond(self, content):        
        handler = self.get_content_handler(content)
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

