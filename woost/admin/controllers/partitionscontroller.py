"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Any

import cherrypy
from cocktail.jsonutils import json_object
from cocktail.controllers import Controller, json_out

from woost.admin import partitioning


class PartitionsController(Controller):

    @json_out
    def __call__(self, method_name, value=None):

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

        return data

    def export_partition(
            self,
            part_method: partitioning.PartitioningMethod,
            value: Any) -> json_object:

        return {
            "value": part_method.serialize_value(value),
            "label": part_method.translate_value(value)
        }

