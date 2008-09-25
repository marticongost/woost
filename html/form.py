#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from magicbullet.modeling import getter, ListWrapper
from magicbullet.translations import translate
from magicbullet.schema import Member, Boolean, Reference
from magicbullet.html.element import Element
from magicbullet.html.datadisplay import DataDisplay
from magicbullet.html.textbox import TextBox
from magicbullet.html.checkbox import CheckBox
from magicbullet.html.selectors import DropdownSelector


class Form(Element, DataDisplay):

    tag = "form"

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        DataDisplay.__init__(self)
        self.set_member_type_display(Member, TextBox)
        self.set_member_type_display(Boolean, CheckBox)
        self.set_member_type_display(Reference, DropdownSelector)
        self.__groups = []
        self.groups = ListWrapper(self.__groups)

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
            if self.__groups:                
                members = self.displayed_members

                for group in self.__groups:

                    fieldset = self.create_fieldset(group)
                    self.fields.append(fieldset)
                    setattr(self, group.id + "_group", fieldset)

                    remaining_members = []

                    for member in members:
                        if group.matches(member):
                            field_entry = self.create_field(member)
                            fieldset.append(field_entry)
                        else:
                            remaining_members.append(member)

                    members = remaining_members
            else:
                for member in self.displayed_members:
                    field_entry = self.create_field(member)
                    self.fields.append(field_entry)
    
    def create_fieldset(self, group):

        fieldset = Element("fieldset")
        fieldset.add_class(group.id)
        
        fieldset.legend = Element("legend")
        fieldset.legend.append(translate(self.schema.name + "." + group.id))
        fieldset.append(fieldset.legend)

        return fieldset

    def create_field(self, member):
        
        # Container
        field_entry = Element()
        field_entry.add_class("field")
        field_entry.add_class(member.name)
        
        # Label
        field_entry.label = self.create_field_label(member)
        field_entry.append(field_entry.label)

        # Control
        field_entry.control = self.get_member_display(self.data, member)
        field_entry.append(field_entry.control)

        return field_entry

    def create_field_label(self, member):
        
        label = Element("label")
        label["for"] = member.name
        label.append(self.get_member_label(member))
        
        return label

    def add_group(self, group):
        self.__groups.append(group)


class FormGroup(object):

    def __init__(self, id, members_filter):        
        self.__id = id
        self.__members_filter = members_filter

        if callable(members_filter):
            self.__match_expr = members_filter
        else:
            members = set(self._normalize_member(member)
                          for member in members_filter)

            self.__match_expr = \
                lambda member: self._normalize_member(member) in members

    @getter
    def id(self):
        return self.__id

    @getter
    def members_filter(self):
        return self.__members_filter

    def matches(self, member):
        return self.__match_expr(member)

