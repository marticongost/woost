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
        cls = self.__class__
        self.set_member_display("element", cls.display_element)
        self.set_member_sortable("element", False)
        self.set_member_type_display(Reference, cls.display_reference)

    def repr_value(self, item, member, value):
        if value is None:
            return "-"
        else:
            return translate(value, default = value)

    def display_element(self, item, member):
        
        display = Element("label")
        display["for"] = self["name"] + "_selection_" + str(item.id)
        display.append(translate(item))

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

