#-*- coding: utf-8 -*-
"""
Provides the CMS subclass used to customize the behavior of the site.
"""
import cherrypy
from pkg_resources import resource_filename
from sitebasis.controllers.application import CMS


class _PROJECT_NAME_CMS(CMS):

    application_path = resource_filename("_PROJECT_MODULE_", None)
        
    class ApplicationContainer(CMS.ApplicationContainer):        
        _PROJECT_MODULE__resources = cherrypy.tools.staticdir.handler(
            section = "_PROJECT_MODULE_",
            dir = resource_filename("_PROJECT_MODULE_.views", "resources")
        )

