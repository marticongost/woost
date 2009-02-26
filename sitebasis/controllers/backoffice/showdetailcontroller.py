#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2009
"""
from cocktail.modeling import cached_getter
from cocktail.schema import Adapter
from sitebasis.models import Language
from sitebasis.controllers.backoffice.editcontroller import EditController


class ShowDetailController(EditController):

    section = "show_detail"

    @cached_getter
    def detail_schema_adapter(self):
        adapter = Adapter()
        adapter.exclude([
            member.name
            for member in self.stack_node.content_type.members().itervalues()
            if not member.visible
        ])
        adapter.exclude(["translations"])
        return adapter

    @cached_getter
    def detail_schema(self):
        content_type = self.stack_node.content_type
        adapter = self.detail_schema_adapter
        schema = adapter.export_schema(content_type)
        schema.name = content_type.name + "Detail"
        return schema

    @cached_getter
    def view_class(self):
        return self.stack_node.item.show_detail_view
    
    @cached_getter
    def output(self):
        node = self.stack_node
        node.import_form_data(node.form_data, node.item)

        output = EditController.output(self)
        # TODO: Add a translation selector
        output["translations"] = Language.codes
        output["detail_schema"] = self.detail_schema
        return output

