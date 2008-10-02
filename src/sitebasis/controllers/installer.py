#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import os
import cherrypy
from cocktail import schema
from cocktail.translations import set_language
from cocktail.html.templates import TemplateLoader
from cocktail.controllers import read_form
from sitebasis import __file__ as sitebasis_file
from sitebasis.translations import installerstrings


class Installer(object):

    views_path = os.path.join(os.path.dirname(sitebasis_file), "views")

    resources = cherrypy.tools.staticdir.handler(
        section = "resources",
        root = views_path,
        dir = "resources"
    )

    def __init__(self):
        self._templates = TemplateLoader()
        self._templates.paths.append(self.views_path)

    @cherrypy.expose
    def index(self, **params):

        set_language("en")
        submitted = params.pop("submit", False)
        errors = []
        
        form_schema = schema.Schema(
            name = "Installer",
            members = [
                schema.String(
                    name = "project_name",
                    required = True,
                    format = r"^[a-z_][a-z_0-9]*$"
                ),
                schema.String(
                    name = "project_path",
                    required = True
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

        if submitted:
            read_form(form_schema, form_data)
            errors = list(form_schema.get_errors(form_data))

            if not errors:
                try:
                    if os.path.exists(form_data["project_path"]):
                        raise InstallFolderExists()
                except Exception, ex:
                    errors.append(ex)
            
            # TODO: Execute installation
            # TODO: Add more validations (ie. directory exists)
        else:
            form_schema.init_instance(form_data)

        view = self._templates.new("Installer.xml")
        view.submitted = submitted
        view.schema = form_schema
        view.data = form_data
        view.errors = errors
        return view.render_page()

    def run(self):
        cherrypy.quickstart(self, "/")


class InstallFolderExists(Exception):
    pass

