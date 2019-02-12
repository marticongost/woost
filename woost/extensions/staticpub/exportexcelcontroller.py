#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import mimetypes
import cherrypy
from cStringIO import StringIO
from cocktail.translations import translations
from cocktail import schema
from cocktail.schema.io import default_msexcel_exporter
from cocktail.controllers import (
    Controller,
    request_property,
    get_parameter,
    file_publication
)
from woost import app
from .export import Export, export_task_schema
from .exportpermission import ExportPermission


class ExportExcelController(Controller):

    @request_property
    def export(self):
        return get_parameter(
            schema.Reference("export", type = Export)
        )

    def __call__(self, **kwargs):

        if self.export is None:
            raise cherrypy.NotFound()

        app.user.require_permission(
            ExportPermission,
            destination = self.export.destination
        )

        buffer = StringIO()
        workbook = default_msexcel_exporter.create_workbook(
            self.export.tasks.values(),
            export_task_schema
        )
        workbook.save(buffer)
        buffer.seek(0)

        return file_publication.serve_file(
            buffer,
            content_type = mimetypes.types_map.get(".xls"),
            disposition = "attachment",
            name = translations(self.export) + ".xls"
        )

