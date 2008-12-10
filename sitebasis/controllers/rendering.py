#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import cherrypy
from sitebasis.models import Site
from sitebasis.controllers.module import Module


class RenderingModule(Module):

    default_engine = "cocktail"      
    default_format = "html"
    
    def __init__(self, *args, **kwargs):
        Module.__init__(self, *args, **kwargs)
        self.__engines = {}

    def render(self, template_name, template_format = None, **values):
        
        # Rendering engine
        engine_name = cherrypy.config.get(
            "rendering.engine",
            self.default_engine)

        engine = self.__engines.get(engine_name)

        if engine is None:
            engine_type = buffet.available_engines[template_engine]
            engine = \
                engine_type(None, self.engine_options.get(template_engine))
            self.__engines[engine_type] = engine
 
        # Rendering format
        if template_format is None:
            template_format = \
                cherrypy.config.get("format", self.default_format)

        # Pass the request context to the template
        request = cherrypy.request
        cms = request.cms
        values.setdefault("cms", cms)
        values.setdefault("site", Site.main)
        values.setdefault("user", cms.authentication.user)
        values.setdefault("document", request.document)

        # Output the result
        return engine.render(
                        values,
                        format = template_format,
                        template = template_name)

