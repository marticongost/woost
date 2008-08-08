#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from genshi.template import TemplateLoader
from magicbullet.translations import translate
from magicbullet.models import Site
from magicbullet.controllers.module import Module


class Rendering(Module):

    loader_options = {"auto_reload": True}
    format = "html"
    doctype = "html"

    def attach(self, application):
        
        Module.attach(self, application)
        
        self.template_loader = TemplateLoader(
            self.application.views_path,
            **self.loader_options
        )

    def render(self, template_name, **values):
        
        template = self.template_loader.load(template_name + ".html")
                
        values.setdefault("translate", translate)
        values.setdefault("user", self.application.authentication.user)
        values.setdefault("site", Site.main)
        values.setdefault("cms", self.application)

        return template.generate(**values).render(
            self.format,
            doctype = self.doctype)


