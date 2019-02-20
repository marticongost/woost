#-*- coding: utf-8 -*-
"""
(X)HTML templates for the CMS backend application.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from pkg_resources import resource_filename
from cocktail.html import resource_repositories

resource_repositories.define(
    "woost",
    "/resources/woost",
    resource_filename("woost.views", "resources")
)

