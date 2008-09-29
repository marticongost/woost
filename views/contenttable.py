#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from magicbullet.translations import translate
from magicbullet.schema import Reference
from magicbullet.html import Element
from magicbullet.html.table import Table


class ContentTable(Table):
    
    base_url = None

    def __init__(self, *args, **kwargs):
        Table.__init__(self, *args, **kwargs)
        self.set_member_sortable("element", False)
        self.set_member_type_display(
            Reference, self.__class__.display_reference)

    def _fill_body(self):
    
        for index, item in enumerate(self.data):
            row = self.create_row(index, item)
            self.append(row)
            self._draft_index = 0

            for draft in item.drafts:
                self._draft_index += 1
                row = self.create_row(index, draft)
                self.append(row)

    def create_row(self, index, item):
        
        row = Table.create_row(self, index, item)

        if item.is_draft:
            row.add_class("draft")

        if item.draft_source:
            row.add_class("nested_draft")

        return row

    def repr_value(self, item, member, value):
        if value is None:
            return "-"
        else:
            return translate(value, default = value)

    def display_element(self, item, member):
        
        display = Element("label")
        display["for"] = "selection_" + str(item.id)

        if item.draft_source:
            desc = translate("draft_seq_name",
                index = self._draft_index)
        else:
            desc = translate(item)
        
        display.append(desc)

        for schema in item.__class__.descend_inheritance(True):
            display.add_class(schema.name)

        return display

    def display_reference(self, item, member):

        value = self.get_member_value(item, member)
        
        if value is None:
            display = Element()
        else:
            display = Element("a")
            display["href"] = self.base_url + "/edit" \
                "?content_selection=%d" % value.id
        
        display.append(self.repr_value(item, member, value))

        return display

