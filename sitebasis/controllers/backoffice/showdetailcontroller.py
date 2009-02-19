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
            for member in self.edited_content_type.members().itervalues()
            if not member.visible
        ])
        adapter.exclude(["translations"])
        return adapter

    @cached_getter
    def detail_schema(self):
        adapter = self.detail_schema_adapter
        schema = adapter.export_schema(self.edited_content_type)
        schema.name = self.edited_content_type.name + "Detail"
        return schema

    @cached_getter
    def view_class(self):
        return (self.edited_item or self.edited_content_type).show_detail_view
    
    @cached_getter
    def output(self):
        output = EditController.output(self)
        # TODO: Add a translation selector
        output["translations"] = Language.codes
        output["detail_schema"] = self.detail_schema
        return output

