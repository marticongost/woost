#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.html import templates
from cocktail.html.uigeneration import (
    UIGenerator,
    EditControlGenerator,
    default_display,
    default_edit_control,
    default_search_control
)

# Custom read only display for the backoffice
#------------------------------------------------------------------------------
def _collection_backoffice_display(
    ui_generator,
    obj,
    member,
    value,
    **context
):
    if member.is_persistent_relation:
        return "woost.views.ContentList"

backoffice_display = UIGenerator(
    "backoffice_display",
    base_ui_generators = [default_display],
    member_type_displays = {
        schema.Collection: _collection_backoffice_display
    }
)

# Custom editable display for the backoffice
#------------------------------------------------------------------------------
def _collection_backoffice_edit_control(
    ui_generator,
    obj,
    member,
    value,
    **context
):
    if member.is_persistent_relation:
        return "woost.views.ItemCollectionEditor"
    else:
        return "cocktail.html.CollectionEditor"

def _reference_backoffice_edit_control(
    ui_generator,
    obj,
    member,
    value,
    **context
):
    if member.class_family is not None:
        display = templates.new("woost.views.ContentTypePickerDropdown")
        display.content_type_picker.root = member.class_family
        return display
    else:
        return "woost.views.ItemSelector"

backoffice_edit_control = EditControlGenerator(
    "backoffice_edit_control",
    base_ui_generators = [default_edit_control],
    member_type_displays = {
        schema.Collection: _collection_backoffice_edit_control,
        schema.Reference: _reference_backoffice_edit_control,
        schema.HTML: "woost.views.RichTextEditor"
    }
)

# Custom search controls for the backoffice
#------------------------------------------------------------------------------
backoffice_search_control = EditControlGenerator(
    "backoffice_search_control",
    base_ui_generators = [
        default_search_control,
        backoffice_edit_control
    ]
)

