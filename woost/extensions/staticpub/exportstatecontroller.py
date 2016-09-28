#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from json import dumps
import cherrypy
from cocktail.translations import translations, translate_locale
from cocktail import schema
from cocktail.controllers import Controller, get_parameter, request_property
from woost.models.utils import any_translation
from .export import Export


class ExportStateController(Controller):

    def __call__(self, **kwargs):
        cherrypy.response.headers["Content-Type"] = "application/json"
        data = {
            "exports": dict(
                (str(export.id), self.get_export_data(export))
                for export in self.exports
            )
        }
        return dumps(data)

    @request_property
    def exports(self):
        return get_parameter(
            schema.Collection(
                "exports",
                type = set,
                items = schema.Reference(
                    type = Export,
                    required = True
                ),
                min = 1
            ),
            errors = "raise"
        )

    def get_export_data(self, export):
        task_records = []
        record = {
            "state": export.state
        }

        total_tasks = 0
        pending = 0
        successes = 0
        failures = 0

        for task in export.tasks.itervalues():
            total_tasks += 1
            task_state = task["state"]

            if task_state == "pending":
                pending += 1
            elif task_state == "success":
                successes += 1
            elif task_state == "failed":
                failures += 1

        record["progress"] = float(successes + failures) / total_tasks

        if export.state == "completed":
            record["summary"] = translations(
                "woost.extensions.staticpub.export.Export.tasks_summary",
                pending = pending,
                successes = successes,
                failures = failures
            )
        else:
            record["summary"] = ""

        return record

