#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
import cherrypy
from cocktail.html.resources import SASS
from woost import app
from woost.models import Configuration, Style
from woost.controllers.publishablecontroller import PublishableController


class StylesController(PublishableController):

    def _produce_content(self, backoffice = False):

        config = Configuration.instance
        website = app.website

        for style in Style.select():

            declarations = (backoffice and style.admin_declarations) or style.declarations

            sass_init = config.common_styles_initialization or ""
            sass_init += website.common_styles_initialization or ""
            sass_init += style.declarations_initialization or ""

            sass_code = "%s.%s{\n%s\n}" % (
                sass_init,
                style.class_name,
                declarations or ""
            )

            yield SASS.compile(string = sass_code)
            yield "\n"

