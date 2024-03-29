#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.schema import Collection, Reference
from cocktail.translations import translations
from cocktail.html import Element, templates

Form = templates.get_class("cocktail.html.Form")


class ContentForm(Form):

    table_layout = False

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.set_member_type_display(Collection, self._get_collection_display)
        self.set_member_type_display(Reference, self._get_reference_display)

    def _resolve_member_display(self, obj, member):

        display = getattr(member, "edit_control", None)
        
        if display is None:
            display = Form._resolve_member_display(self, obj, member)

        return display

    def _get_collection_display(self, obj, member):
        if member.is_persistent_relation:
            return "woost.views.ItemCollectionEditor"
        else:
            return "cocktail.html.CollectionEditor"

    def _get_reference_display(self, obj, member):
        if member.class_family is not None:
            display = templates.new("woost.views.ContentTypePickerDropdown")
            display.content_type_picker.root = member.class_family
        else:
            display = "woost.views.ItemSelector"
    
        return display

    def create_fieldset(self, group):
        fieldset = Form.create_fieldset(self, group)
        fieldset.set_client_param("group", group)
        return fieldset

    def get_group_label(self, group):

        label = Form.get_group_label(self, group)

        if not label and (not group or group == "default"):
            label = translations(self.schema.original_member.name)
        
        return label

