"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.controllers import Controller, Dispatcher

from woost.admin.views import require_view, UnavailableViewError


class ViewsController(Controller):

    def resolve(self, path: Dispatcher.PathProcessor) -> Controller:

        if not path:
            return None

        view_name = path[0]

        try:
            view = require_view(view_name)
        except (KeyError, UnavailableViewError):
            raise cherrypy.HTTPError(400, "Invalid view: " + view_name)

        path.pop(0)

        controller = view.controller()
        controller.view = view
        return controller

