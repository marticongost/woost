#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import json
import cherrypy
from ZODB.POSException import ConflictError
from cocktail.events import monitor_thread_events
from cocktail.pkgutils import get_full_name
from cocktail.translations import translations
from cocktail import schema
from cocktail.schema.exceptions import ValidationError, ValueRequiredError
from cocktail.persistence import datastore
from cocktail.controllers import Controller
from cocktail.controllers.csrfprotection import no_csrf_token_injection
from woost import app
from woost.models import (
    changeset_context,
    Item,
    CreatePermission,
    ModifyPermission,
    DeletePermission
)
from woost.admin.dataexport import Export
from woost.admin.dataimport import Import
from .utils import resolve_object_ref, get_model_from_state


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
        dry_run = data.get("dry_run", False)

        response_data = {"request": data}

        # Apply and commit the changes
        if dry_run:
            imports, created, modified, deleted, errors = \
                self._execute(data, True)
        else:
            attempt = 1

            while True:

                with changeset_context(app.user):
                    imports, created, modified, deleted, errors = \
                        self._execute(data)

                if errors:
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

                    break

        # Return the updated state
        cherrypy.response.headers["Content-Type"] = \
            "application/json; charset=utf-8"

        if errors:
            response_data["errors"] = errors
        else:
            response_data["changes"] = self._export_changes(
                created,
                modified,
                deleted
            )

        return json.dumps(response_data)

    def _execute(self, data, dry_run = False):

        states = data.get("objects")
        delete_ids = data.get("delete")

        if not states and not delete_ids:
            raise cherrypy.HTTPError(
                400,
                "Must specify one or more actions to perform"
            )

        # Use monitor_thread_events() to setup temporary event handlers,
        # limited to this thread
        created = set()
        modified = set()
        deleted = set()

        def record_created(e):
            modified.discard(e.instance)
            created.add(e.instance)

        def record_modified(e):
            if e.source not in created and e.member.visible:
                modified.add(e.source)

        def record_deleted(e):
            modified.discard(e.source)
            if e.source in created:
                created.remove(e.source)
            else:
                deleted.add(e)

        with monitor_thread_events(
            (Item.instantiated, record_created),
            (Item.changed, record_modified),
            (Item.deleted, record_deleted)
        ):
            imports = []
            errors = {}
            user = app.user

            if states:
                for state in states:
                    new = state.get("_new")
                    id = state.get("id")

                    if not new and not id:
                        raise cherrypy.HTTPError(
                            "Expected a _new flag or the id of an existing "
                            "object"
                        )

                    if new:
                        model = get_model_from_state(state)
                        obj = model()
                        user.require_permission(
                            CreatePermission,
                            target = obj
                        )
                    else:
                        obj = resolve_object_ref(id)
                        user.require_permission(
                            ModifyPermission,
                            target = obj
                        )

                    imports.append(self._import_object(obj, state))

                    obj_errors = self._export_errors(obj, dry_run)
                    if obj_errors:
                        errors[id] = obj_errors

                    if not dry_run:
                        obj.insert()

            if delete_ids:
                for id in delete_ids:
                    obj = resolve_object_ref(id)
                    user.require_permission(
                        DeletePermission,
                        target = obj
                    )
                    obj.delete()

        return imports, created, modified, deleted, errors

    def _import_object(self, obj, data, **kwargs):
        return Import(
            data,
            obj = obj,
            user = app.user,
            **kwargs
        )

    def _export_changes(self, created, modified, deleted):
        exp = Export()
        return {
            "created":
                dict(
                    (str(obj.id), exp.export_object(obj))
                    for obj in created
                ),
            "modified":
                dict(
                    (str(obj.id), exp.export_object(obj))
                    for obj in modified
                ),
            "deleted":
                dict(
                    (str(obj.id), exp.export_object(obj, ref = True))
                    for obj in deleted
                )
        }

    def _export_errors(self, obj, dry_run):
        return [
            self._export_error(error)
            for error in obj.__class__.get_errors(obj)
            if not self._should_ignore_error(error)
        ]

    def _should_ignore_error(self, error):
        return (
            isinstance(error, ValueRequiredError)
            and isinstance(error.member, schema.Reference)
            and error.member.related_end
            and error.member.related_end.integral
        )

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

