#-*- coding: utf-8 -*-
u"""
Provides the CMS subclass used to customize the behavior of the site.
"""
from woost.controllers.cmscontroller import CMSController


class --SETUP-WEBSITE--CMSController(CMSController):

    _cp_config = CMSController.copy_config()
    _cp_config["rendering.engine"] = "cocktail"

    class ApplicationContainer(CMSController.ApplicationContainer):
        pass

