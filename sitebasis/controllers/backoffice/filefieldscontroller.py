#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
import os
from shutil import move
import cherrypy
from cocktail.modeling import cached_getter
from cocktail import schema
from cocktail.controllers.fileupload import FileUpload
from sitebasis.controllers.backoffice.itemfieldscontroller \
    import ItemFieldsController
from sitebasis.controllers import CMS


class FileFieldsController(ItemFieldsController):

    @cached_getter
    def form_adapter(self):
        adapter = ItemFieldsController.form_adapter(self)
        adapter.exclude(["resource_type"])
        adapter.export_rules.add_rule(ExportUploadInfo())
        adapter.import_rules.add_rule(ImportUploadInfo())
        return adapter

    @cached_getter
    def form_schema(self):
        form_schema = ItemFieldsController.form_schema(self)
        form_schema.add_member(
            FileUpload("upload",
                required = True,
                hash_algorithm = "md5",
                get_file_destination = lambda upload: self.temp_file_path                    
            )
        )
        return form_schema

    @cached_getter
    def form_data(self):

        stack_upload_data = self.stack_node.form_data \
            and self.stack_node.form_data.get("upload")

        form_data = ItemFieldsController.form_data(self)

        if not form_data.get("upload") and stack_upload_data:
            form_data["upload"] = stack_upload_data

        return form_data

    @cached_getter
    def temp_file_path(self):
        return os.path.join(
            self.context["cms"].upload_path,
            "temp",
            "%s-%s-%s" % (
                self.stack_node.generated_id,
                cherrypy.session.id,
                self.edit_stack.to_param()
            )
        )


class ExportUploadInfo(schema.Rule):

    def adapt_object(self, context):
        file_name = context.get("file_name")
        
        if file_name:
            context.set("upload", {
                "file_name": file_name,
                "mime_type": context.get("mime_type"),
                "file_size": context.get("file_size"),
                "file_hash": context.get("file_hash")
            })


class ImportUploadInfo(schema.Rule):

    def adapt_object(self, context):

        context.consume("upload")
        upload = context.get("upload", None)

        if upload:
            context.set("file_name", schema.get(upload, "file_name"))
            context.set("mime_type", schema.get(upload, "mime_type"))
            context.set("file_size", schema.get(upload, "file_size"))
            context.set("file_hash", schema.get(upload, "file_hash"))


@CMS.saving_item.append
def move_temp_file(event):
    # Move the uploaded file to its permanent location
    src = event.controller.temp_file_path
    dest = event.item.file_path

    if os.path.exists(dest):
        os.remove(dest)

    move(src, dest)

