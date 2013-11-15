#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.controllers import Controller, request_property


class PasswordChangeBlockController(Controller):

    @request_property
    def output(self):
        output = Controller.output(self)
        output["forms"] = cherrypy.request.handler_chain[-1].forms
        return output


class PasswordChangeConfirmationBlockController(Controller):

    @request_property
    def output(self):
        output = Controller.output(self)
        controller_output = cherrypy.request.handler_chain[-1].output
        for key in ("identifier", "hash", "forms"):
            output[key] = controller_output[key]
        return output

