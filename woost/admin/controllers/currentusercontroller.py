#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import json
import cherrypy
from cocktail.controllers import Controller
from cocktail.controllers.csrfprotection import no_csrf_token_injection
from woost import app
from woost.admin.dataexport import Export


class CurrentUserController(Controller):

    @no_csrf_token_injection
    def __call__(self):

        cherrypy.response.headers["Content-Type"] = \
            "application/json; charset=utf-8"

        response_data = Export().export_object(app.user)
        return json.dumps(response_data)

