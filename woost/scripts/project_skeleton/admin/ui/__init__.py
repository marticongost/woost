#-*- coding: utf-8 -*-
"""Site specific admin UI components.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost import app
from cocktail.ui import components

app.add_resources_repository("--SETUP-PACKAGE--.admin.ui", app.path("admin", "ui", "resources"))
components.theme.add_location("--SETUP-PACKAGE--.admin.ui://styles")

