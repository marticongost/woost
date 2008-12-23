#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.translations import translate
from cocktail.schema import Collection, Reference
from cocktail.html import Element, templates

Form = templates.get_class("cocktail.html.Form")
DropdownSelector = templates.get_class("cocktail.html.DropdownSelector")


class ContentForm(Form):

    item_selector_threshold = 10

    def _resolve_member_display(self, obj, member):

        display = getattr(member, "edit_control", None)
        
        if display is None:

            if isinstance(member, Reference):
                if member.class_family is not None:
                    display = \
                        templates.new("sitebasis.views.ContentTypePicker")
                    display.root = member.class_family
                elif len(member.type.index) <= self.item_selector_threshold:
                    display = ItemDropdownSelector
                else:
                    display = "sitebasis.views.ItemSelector"
            else:
                display = Form._resolve_member_display(self, obj, member)

        return display


class ItemDropdownSelector(DropdownSelector):

    def get_item_value(self, item):
        return item.id

