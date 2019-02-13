#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import json
import cherrypy
from cocktail.translations import translations
from cocktail.controllers import HTTPMethodController
from woost import app
from woost.models import (
    Configuration,
    Website,
    PermissionExpression,
    ReadPermission
)


class SettingsScopesController(HTTPMethodController):

    @cherrypy.expose
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

        cherrypy.response.headers["Content-Type"] = \
            "application/json; charset=utf-8"

        return json.dumps(scopes)

