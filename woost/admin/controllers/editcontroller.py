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
from cocktail.persistence import datastore, InstanceNotFoundError
from cocktail.controllers import Controller, request_property
from cocktail.controllers.csrfprotection import no_csrf_token_injection
from woost import app
from woost.models import Item, ReadPermission
from woost.models.utils import get_model_dotted_name
from woost.admin.models.dataexport import Export
from woost.admin.models.dataimport import import_object_data


class EditController(Controller):

    creating_new_object = False
    max_transaction_attempts = 3

    @no_csrf_token_injection
    def __call__(
        self,
        target,
        action = "save",
        deleted_translations = None
    ):
        # Create a new object, or load an existing one
        obj = self._resolve_target(target)

        # Require read permission for the object
        app.user.require_permission(
            ReadPermission,
            target = obj.__class__
        )

        # Load JSON data from the request body
        length = int(cherrypy.request.headers["Content-Length"])
        json_string = cherrypy.request.body.read(length)
        data = json.loads(json_string)

        # Only report validation errors
        if action == "validate":
            self._import_object(obj, data, deleted_translations)
            obj.insert()
            response_data = {
                "state": data,
                "errors": self._export_errors(obj)
            }
        # Commit the changes
        elif action == "save":
            attempt = 1

            while True:

                # Import data
                self._import_object(obj, data, deleted_translations)
                obj.insert()

                # Validate errors
                errors = self._export_errors(obj)
                if errors:
                    response_data = {"state": data, "errors": errors}
                    break

                try:
                    datastore.commit()
                except ConflictError, conflict_error:
                    if attempts > self.max_transaction_attempts:
                        raise
                    attempt += 1
                    datastore.sync()
                else:
                    response_data = {
                        "state": self._export_object(obj),
                        "errors": []
                    }
                    break
        else:
            raise cherrypy.HTTPError(404, "Invalid action: " + action)

        # Return the updated state
        cherrypy.response.headers["Content-Type"] = \
            "application/json; charset=utf-8"

        return json.dumps(response_data)

    def _resolve_target(self, target):

        # Create a new object
        if self.creating_new_object:
            for cls in Item.schema_tree():
                if get_model_dotted_name(cls) == target:
                    return cls()
            else:
                raise cherrypy.HTTPError(404, "Unknown model: " + target)

        # Update an existing object
        else:
            try:
                return Item.require_instance(int(target))
            except (ValueError, InstanceNotFoundError):
                raise cherrypy.HTTPError(404, "Invalid object id: " + target)

    def _import_object(self, obj, data, deleted_translations = ()):
        import_object_data(
            obj,
            data,
            deleted_translations = deleted_translations,
            user = app.user
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

