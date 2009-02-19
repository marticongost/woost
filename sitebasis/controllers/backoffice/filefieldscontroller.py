#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.modeling import cached_getter
from cocktail import schema
from cocktail.controllers.fileupload import FileUpload
from sitebasis.controllers.backoffice.itemfieldscontroller \
    import ItemFieldsController


class FileFieldsController(ItemFieldsController):

    @cached_getter
    def form_adapter(self):
        adapter = ItemFieldsController.form_adapter(self)
        adapter.exclude(["resource_type"])
        adapter.import_rules.add_rule(ExtractUploadInfo())
        return adapter

    @cached_getter
    def form_schema(self):
        form_schema = ItemFieldsController.form_schema(self)
        form_schema.add_member(
            FileUpload("upload",
                required = True,
                get_file_destination = lambda upload:
                    self.context["cms"].get_file_upload_path(
                        self.stack_node.generated_id
                    )
            )
        )
        return form_schema

    @cached_getter
    def form_data(self):

        stack_upload_data = self.stack_node.form_data \
            and self.stack_node.form_data.get("upload")

        form_data = ItemFieldsController.form_data(self)

        from styled import styled
        print styled(form_data, "brown")
        print styled(stack_upload_data, "violet")

        if not form_data.get("upload") and stack_upload_data:
            form_data["upload"] = stack_upload_data
            print styled(form_data, "turquoise")

        return form_data


class ExtractUploadInfo(schema.Rule):

    def adapt_object(self, context):

        context.consume("upload")
        upload = context.get("upload", None)

        if upload:
            context.set("file_name", schema.get(upload, "file_name"))
            context.set("mime_type", schema.get(upload, "mime_type"))

