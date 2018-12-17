#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import json
import cherrypy
from ZODB.POSException import ConflictError
from cocktail.pkgutils import get_full_name
from cocktail.translations import translations
from cocktail.schema.exceptions import ValidationError
from cocktail.persistence import datastore
from cocktail.controllers import Controller
from cocktail.controllers.csrfprotection import no_csrf_token_injection
from woost import app
from woost.models import changeset_context
from woost.admin.dataexport import Export
from woost.admin.dataimport import Import
from .utils import resolve_object_ref


class TransactionController(Controller):

    max_transaction_attempts = 3

    @no_csrf_token_injection
    def __call__(self):

        if cherrypy.request.method != "POST":
            raise cherrypy.HTTPError(405, "Expected a POST request")

        if cherrypy.request.headers["Content-Type"] != "application/json":
            raise cherrypy.HTTPError(400, "Expected an application/json payload")

        # Load JSON data from the request body
        length = int(cherrypy.request.headers["Content-Length"])
        json_string = cherrypy.request.body.read(length)
        data = json.loads(json_string)

        # Apply and commit the changes
        attempt = 1

        while True:

            errors = {}
            modified_objects = []
            imports = []

            # Import data
            # TODO: support "insert" and "delete" keys
            with changeset_context(app.user):
                modify_states = data.get("modify")
                if modify_states:
                    for state in modify_states:
                        id = state["id"]
                        obj = resolve_object_ref(id)
                        modified_objects.append(obj)
                        imports.append(self._import_object(obj, state))
                        obj_errors = self._export_errors(obj)
                        if obj_errors:
                            errors[id] = obj_errors

            if errors:
                response_data = {"transaction": data, "errors": errors}
                break

            try:
                datastore.commit()
            except ConflictError, conflict_error:
                if attempts > self.max_transaction_attempts:
                    raise
                attempt += 1
                datastore.sync()
            else:
                for imp in imports:
                    imp.commit_successful()
                response_data = {
                    "modified": dict(
                        (obj.id, self._export_object(obj))
                        for obj in modified_objects
                    ),
                    "errors": {}
                }
                break

        # Return the updated state
        cherrypy.response.headers["Content-Type"] = \
            "application/json; charset=utf-8"

        return json.dumps(response_data)

    def _import_object(self, obj, data, **kwargs):
        return Import(
            data,
            obj = obj,
            user = app.user,
            **kwargs
        )

    def _export_object(self, obj):
        return Export().export_object(obj)

    def _export_errors(self, obj):
        return [
            self._export_error(error)
            for error in obj.__class__.get_errors(obj)
        ]

    def _export_error(self, error):

        record = {
            "type": get_full_name(error.__class__),
            "label": translations(error)
        }

        if isinstance(error, ValidationError):
            language = error.language
            if language:
                record["language"] = language

            record["members"] = list(set(
                member.name
                for member in error.invalid_members
                if member.name
            ))

        return record

