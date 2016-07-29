#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from json import dumps
import cherrypy
from cocktail import schema
from cocktail.translations import translations, translate_locale
from cocktail.urls import URL
from cocktail.html.readonlydisplay import read_only_display
from cocktail.persistence import transaction
from cocktail.controllers import (
    request_property,
    get_parameter
)
from woost import app
from woost.models import (
    LocaleMember,
    Configuration,
    Publishable,
    Document,
    changeset_context
)
from woost.models.utils import any_translation
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from .destination import Destination
from .export import Export
from .exportpermission import ExportPermission
from .utils import iter_exportable_languages

translations.load_bundle("woost.extensions.staticpub.exportcontroller")


class ExportController(BaseBackOfficeController):
    view_class = "woost.extensions.staticpub.BackOfficeStaticPubExportView"

    @request_property
    def destinations(self):
        user = app.user
        return [
            destination
            for destination in Destination.select()
            if user.has_permission(ExportPermission, destination = destination)
        ]

    @request_property
    def submitted(self):
        return "export_action" in cherrypy.request.params

    @request_property
    def export_data(self):
        return get_parameter(
            self.export_schema,
            undefined = "set_none" if self.submitted else "set_default",
            implicit_booleans = self.submitted
        )

    @request_property
    def export_schema(self):

        selection_member = schema.Collection(
            "selection",
            items = schema.Reference(type = Publishable),
            edit_control = "woost.extensions.staticpub.ExportSelectionDisplay"
        )

        members = [
            schema.Reference(
                "destination",
                type = Destination,
                required = True,
                default =
                    Configuration.instance.staticpub_default_dest
                    or self.destinations[0],
                edit_control =
                    "cocktail.html.RadioSelector"
                    if len(self.destinations) > 1
                    else read_only_display
            ),
            selection_member,
            schema.Boolean(
                "invalidated_content_only",
                required = True,
                default = True
            )
        ]

        if get_parameter(selection_member):
            members.append(
                schema.Boolean(
                    "include_descendants",
                    required = True,
                    default = True
                )
            )

        members.extend([
            schema.String(
                "language_mode",
                required = True,
                default = "all",
                enumeration = ["all", "include", "exclude"],
                edit_control = "cocktail.html.RadioSelector"
            ),
            schema.Collection(
                "language_subset",
                items = LocaleMember(
                    required = True,
                    enumeration = [
                        language
                        for language in Configuration.instance.languages
                        if language
                        not in Configuration.instance.virtual_languages
                    ]
                ),
                edit_control = "cocktail.html.SplitSelector"
            ),
            schema.Boolean(
                "include_neutral_language",
                required = True,
                default = True
            )
        ])

        return schema.Schema(
            "woost.extensions.staticpub.exportcontroller.ExportController"
            ".export_schema",
            members = members
        )

    def iter_tasks(self):

        data = self.export_data
        destination = data["destination"]
        include_neutral_language = data["include_neutral_language"]
        include_descendants = data.get("include_descendants", False)
        invalidated_content_only = data["invalidated_content_only"]
        language_mode = data["language_mode"]
        language_subset = data["language_subset"]
        include_neutral_language = data["include_neutral_language"]
        selection = (
            data["selection"]
            or Publishable.select(
                Publishable.included_in_static_publication.equal(True)
            )
        )

        visited = set()

        def traverse(publishable_list):

            for publishable in publishable_list:

                if publishable in visited:
                    continue
                else:
                    visited.add(publishable)

                for language in iter_exportable_languages(publishable):

                    if language is None:
                        if not include_neutral_language:
                            continue
                    elif language_mode == "include":
                        if language not in language_subset:
                            continue
                    elif language_mode == "exclude":
                        if language in language_subset:
                            continue

                    if invalidated_content_only:
                        if not destination.get_pending_task(
                            publishable,
                            language
                        ):
                            continue

                    yield "post", publishable, language

                if include_descendants and isinstance(publishable, Document):
                    for item in traverse(publishable.children):
                        yield item

        from cocktail.styled import styled
        print styled(selection, "cyan")
        return traverse(selection)

    def submit(self):

        def create_export():
            with changeset_context(app.user):
                export = Export.new()
                export.destination = self.export_data["destination"]
                for action, publishable, language in self.iter_tasks():
                    export.add_task(action, publishable, language)
            return export

        export = transaction(create_export)
        export.execute_in_subprocess()

        raise cherrypy.HTTPRedirect(
            app.publishable.get_uri(
                path = ["content", str(export.id)]
            )
        )

    @request_property
    def output(self):
        output = BaseBackOfficeController.output(self)
        output["export_schema"] = self.export_schema
        output["export_data"] = self.export_data
        return output

    @cherrypy.expose
    def preview(self, **kwargs):

        cherrypy.response.headers["Content-Type"] = "application/json"

        records = []
        current_publishable = None
        current_record = None
        destination = self.export_data["destination"]
        dest_url = (
            URL(destination.url)
            if destination and destination.url
            else None
        )

        def finish_record():
            if current_record:
                current_record["language_count"] = translations(
                    "woost.extensions.staticpub.exportcontroller."
                    "ExportController.language_count",
                    count = len(current_record["languages"])
                )

        task_count = 0

        for action, publishable, language in self.iter_tasks():
            task_count += 1

            if publishable is not current_publishable:
                finish_record()
                current_publishable = publishable
                current_record = {
                    "publishable": {
                        "id": publishable.id,
                        "label": any_translation(publishable)
                    },
                    "parents": [
                        {
                            "id": parent.id,
                            "label": any_translation(parent)
                        }
                        for parent in publishable.ascend_tree()
                    ],
                    "languages": {}
                }
                records.append(current_record)

            source_url = publishable.get_uri(language = language)
            export_url = destination.get_export_url(source_url)

            current_record["languages"][language or ""] = {
                "action": action,
                "status": "pending",
                "source_url": source_url,
                "export_url": export_url,
                "language_label": translate_locale(language)
            }

        finish_record()
        return dumps({
            "task_count_label": translations(
                "woost.extensions.staticpub.exportcontroller."
                "ExportController.task_count",
                count = task_count
            ),
            "tasks": records
        })

