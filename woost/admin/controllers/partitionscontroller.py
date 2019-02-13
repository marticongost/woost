#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import json
import cherrypy
from cocktail.controllers import Controller
from woost.admin import partitioning


class PartitionsController(Controller):

    def __call__(self, method_name, value = None):

        cherrypy.response.headers["Content-Type"] = "application/json"

        try:
            part_method = partitioning.require_method(method_name)
        except (KeyError, partitioning.UnavailableMethodError):
            raise cherrypy.HTTPError(
                400,
                "Invalid partitioning method: " + method_name
            )

        if value:
            value = part_method.parse_value(value)
            data = self.export_partition(part_method, value)
        else:
            data = [
                self.export_partition(part_method, value)
                for value in list(part_method.values())
            ]

        return json.dumps(data)

    def export_partition(self, part_method, value):
        return {
            "value": part_method.serialize_value(value),
            "label": part_method.translate_value(value)
        }

