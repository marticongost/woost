#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.translations import translations
from cocktail.controllers import Controller
from .listingcontroller import ListingController
from .defaultscontroller import DefaultsController
from .editcontroller import EditController
from .deletecontroller import DeleteController

translations.load_bundle("woost.admin.controllers.datacontroller")


class DataController(Controller):

    defaults = DefaultsController

    def resolve(self, path):

        method = cherrypy.request.method

        if method == "GET":
            return ListingController
        elif method == "PUT":
            controller = EditController()
            controller.creating_new_object = True
            return controller
        elif method == "POST":
            controller = EditController()
            controller.creating_new_object = False
            return controller
        elif method == "DELETE":
            return DeleteController
        elif method == "OPTIONS":
            return self
        else:
            raise cherrypy.HTTPError(405)

    def __call__(self):
        cherrypy.response.headers["Allow"] = "OPTIONS, GET, POST, PUT, DELETE"
        return ""

