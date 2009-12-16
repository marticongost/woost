#-*- coding: utf-8 -*-
u"""
Provides the CMS subclass used to customize the behavior of the site.
"""
import cherrypy
from pkg_resources import resource_filename
from woost.controllers.application import CMS


class _PROJECT_NAME_CMS(CMS):

    application_path = resource_filename("_PROJECT_MODULE_", None)

    _cp_config = CMS.copy_config()
    _cp_config["rendering.engine"] = "_TEMPLATE_ENGINE_"
    _cp_config["rendering.engine_options"] = {
        "mako.directories": [
            resource_filename("_PROJECT_MODULE_", "views"),
            resource_filename("woost", "views")
        ],
        "mako.output_encoding": "utf-8"
    }

    class ApplicationContainer(CMS.ApplicationContainer):        
        _PROJECT_MODULE__resources = cherrypy.tools.staticdir.handler(
            section = "_PROJECT_MODULE__resources",
            dir = resource_filename("_PROJECT_MODULE_.views", "resources")
        )

