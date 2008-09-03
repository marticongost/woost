#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from magicbullet.html.element import Element
from magicbullet.html.datadisplay import DataDisplay
from magicbullet.html.textbox import TextBox
from magicbullet.html.checkbox import CheckBox
from magicbullet.html.selectors import DropdownSelector
from magicbullet.translations import translate
from magicbullet.schema import Member, Boolean, Reference

class Form(Element, DataDisplay):

    tag = "form"

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        DataDisplay.__init__(self)
        self.set_member_type_display(Member, TextBox)
        self.set_member_type_display(Boolean, CheckBox)
        self.set_member_type_display(Reference, DropdownSelector)

    def _build(self):

        self.fields = Element()
        self.fields.add_class("fields")
        self.append(self.fields)

        self.buttons = Element()
        self.buttons.add_class("buttons")
        self.append(self.buttons)

        self.submit_button = Element("button")
        self.submit_button["type"] = "submit"
        self.submit_button.append(translate("Submit"))
        self.append(self.submit_button)

    def _ready(self):
        self._fill_fields()

    def _fill_fields(self):
        if self.schema:
            for member in self.displayed_members:
                field_entry = self.create_field(member)
                self.fields.append(field_entry)
    
    def create_field(self, member):
        
        # Container
        field_entry = Element()
        field_entry.add_class("field")
        field_entry.add_class(member.name)
        
        # Label
        label = self.create_field_label(member)
        field_entry.append(label)

        # Control
        control = self.get_member_display(self.data, member)
        field_entry.append(control)

        return field_entry

    def create_field_label(self, member):
        
        label = Element("label")
        label["for"] = member.name
        label.append(self.get_member_label(member))
        
        return label


