#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.pkgutils import resource_filename
from cocktail.controllers import (
    Controller,
    folder_publisher
)


class CMSResourcesController(Controller):

    cocktail = folder_publisher(
        resource_filename("cocktail.html", "resources")
    )

    cocktail_ui = folder_publisher(
        resource_filename("cocktail.ui", "resources")
    )

