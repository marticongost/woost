#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from pkg_resources import resource_filename
from cocktail.controllers import (
    Controller,
    folder_publisher
)


class CMSResourcesController(Controller):

    cocktail = folder_publisher(
        resource_filename("cocktail.html", "resources")
    )

    woost = folder_publisher(
        resource_filename("woost.views", "resources")
    )

