#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.translations import translations
from cocktail.controllers import HTTPMethodController
from .listingcontroller import ListingController
from .editcontroller import EditController
from .deletecontroller import DeleteController
from .defaultscontroller import DefaultsController

translations.load_bundle("woost.admin.controllers.datacontroller")


class DataController(HTTPMethodController):

    GET = ListingController
    PUT = EditController
    POST = EditController
    DELETE = DeleteController

    defaults = DefaultsController

