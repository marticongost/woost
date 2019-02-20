#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.translations import translations
from cocktail.controllers import HTTPMethodController, json_out
from woost import app
from woost.models import (
    Configuration,
    Website,
    PermissionExpression,
    ReadPermission
)


class SettingsScopesController(HTTPMethodController):

    @cherrypy.expose
    @json_out
    def GET(self):
        scopes = [("config", translations(Configuration.instance))]
        scopes.extend(
            ("website-%s" % website.identifier, translations(website))
            for website in Website.select(
                PermissionExpression(
                    app.user,
                    ReadPermission
                ),
                order = "site_name"
            )
        )
        return scopes

