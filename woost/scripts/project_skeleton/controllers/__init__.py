#-*- coding: utf-8 -*-
u"""
Site specific controllers.
"""
from woost import app
from --SETUP-PACKAGE--.controllers.--SETUP-FLAT_WEBSITE_NAME--cmscontroller import --SETUP-WEBSITE--CMSController

app.add_resources_repository("--SETUP-PACKAGE--", app.path("views", "resources"))

