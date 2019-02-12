#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Pastor <jordi.pastor@whads.com>
"""
import os
import re
import zipfile
from cocktail import schema
from cocktail.translations import translations
from cocktail import schema
from cocktail.controllers import (
    request_property,
    FormProcessor,
    Form,
    FileUpload,
    session,
    reload_request_url
)
from woost import app
from woost.models import File, LocaleMember
from woost.controllers.asyncupload import async_uploader
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController

translations.load_bundle("woost.controllers.backoffice.massfileimportcontroller")

separators_regexp = re.compile(r"[-_.;:\t \|]+")


class MassFileImportController(FormProcessor, BaseBackOfficeController):
    is_transactional = True

    class MassImportForm(Form):

        max_upload_size = "500MB"
        valid_mime_types = ["application/zip"]

        @request_property
        def schema(self):
            form_schema = Form.schema(self)
            form_schema.members_order = [
                "title_scheme",
                "series_title",
                "language_for_titles",
                "normalize_case",
                "normalize_separators",
                "upload"
            ]
            form_schema.add_member(
                schema.String(
                    "title_scheme",
                    required = True,
                    default = "from_file",
                    enumeration = [
                        "from_file",
                        "series",
                        "no_title"
                    ],
                    edit_control = "cocktail.html.RadioSelector"
                )
            )

            def _series_title_min(ctx):
                title_scheme = ctx.get_value("title_scheme", stack_node = -2)
                return 1 if title_scheme == "series" else None

            form_schema.add_member(
                schema.Mapping(
                    "series_title",
                    keys = LocaleMember(),
                    values = schema.String(),
                    min = _series_title_min
                )
            )

            form_schema.add_member(
                LocaleMember(
                    "language_for_titles",
                    required =
                        form_schema.get_member("title_scheme")
                        .equal("from_file")
                )
            )
            form_schema.add_member(
                schema.Boolean(
                    "normalize_case",
                    default = True
                )
            )
            form_schema.add_member(
                schema.Boolean(
                    "normalize_separators",
                    default = True
                )
            )
            form_schema.add_member(
                FileUpload(
                    "upload",
                    required = True,
                    max_size = self.max_upload_size,
                    mime_type_properties = {
                        "enumeration": self.valid_mime_types
                    },
                    async = True,
                    async_uploader = async_uploader,
                    async_upload_url = app.url_mapping.get_url(
                        path = ["async_upload"]
                    )
                )
            )
            return form_schema

        def submit(self):

            Form.submit(self)

            files = File.import_zip_contents(self.data["upload"]["file"])
            file_ids = []

            title_scheme = self.data["title_scheme"]
            if title_scheme == "from_file":
                language_for_titles = self.data["language_for_titles"]
                normalize_case = self.data["normalize_case"]
                normalize_separators = self.data["normalize_separators"]
            elif title_scheme == "series":
                series_title = self.data["series_title"]

            for n, file in enumerate(files):
                file_ids.append(file.id)

                if title_scheme == "from_file":
                    title = os.path.splitext(file.file_name)[0]

                    if normalize_case:
                        title = title.capitalize()

                    if normalize_separators:
                        title = separators_regexp.sub(" ", title)

                    file.set("title", title, language_for_titles)

                elif title_scheme == "series":
                    for lang, title in series_title.iteritems():
                        title = u"%s %d" % (title.strip(), n + 1)
                        file.set("title", title, lang)

            session["mass_file_import_results"] = file_ids

        def after_submit(self):
            reload_request_url()

    @request_property
    def results(self):

        results = None
        file_ids = session.pop("mass_file_import_results", None)

        if file_ids:
            results = []
            for file_id in file_ids:
                file = File.get_instance(file_id)
                if file:
                    results.append(file)

        return results

    @request_property
    def view_class(self):
        if self.results:
            return "woost.views.MassFileImportResults"
        else:
            return "woost.views.MassFileImport"

    @request_property
    def output(self):
        output = BaseBackOfficeController.output(self)
        output["results"] = self.results
        return output


