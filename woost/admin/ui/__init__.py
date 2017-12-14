#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from pkg_resources import resource_filename
from cocktail.ui.theme import default_theme
from cocktail.html.resources import resource_repositories

resource_repositories.define(
    "woost.admin.ui",
    "/resources/woost.admin.ui",
    resource_filename("woost.admin.ui", "resources")
)

default_theme.add_location("woost.admin.ui://styles")

