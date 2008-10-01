#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import os
import webbrowser
import cherrypy
from cocktail import schema
from cocktail.translations import set_language
from cocktail.html.templates import TemplateLoader
from sitebasis import __file__ as sitebasis_file


class Installer(object):

    path = os.path.dirname(sitebasis_file)
    views_path = os.path.join(path, "views")

    resources = cherrypy.tools.staticdir.handler(
        section = "resources",
        dir = os.path.join(views_path, "resources")
    )

    def __init__(self):
        self._templates = TemplateLoader()
        self._templates.paths.append(self.views_path)

    @cherrypy.expose
    def index(self):

        set_language("en")
        
        form_schema = schema.Schema(
            members = [
                schema.String(
                    name = "project_name",
                    required = True,
                    format = r"[a-z_][a-z_0-9]*"
                ),
                schema.String(
                    name = "admin_email",
                    required = True,
                    default = "admin@localhost"
                ),
                schema.String(
                    name = "admin_password",
                    required = True,
                    min = 8
                )
            ]
        )

        form_data = {}

        view = self._templates.new("Installer.xml")
        view.schema = form_schema
        view.data = form_data
        return view.render_page()

    def run(self):

        def show_installer():
            webbrowser.open("http://localhost:8080/", True, True)

        cherrypy.engine.subscribe("start", show_installer)
        cherrypy.quickstart(self, "/")

