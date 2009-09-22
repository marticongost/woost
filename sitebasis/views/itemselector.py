#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from cocktail.translations import translations
from cocktail.html import Element, templates
from cocktail.html.databoundcontrol import DataBoundControl
from sitebasis.models import Item


class ItemSelector(Element, DataBoundControl):

    value = None
    _empty_label = None
    
    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        DataBoundControl.__init__(self)

    def _get_empty_label(self):

        if self._empty_label is None:

            if self.member:
                if self.member.required == True:
                    return translations("sitebasis.views.ItemSelector select")
                else:
                    content_type = self.member.type
            else:
                content_type = Item

            for content_type in content_type.descend_inheritance(True):
                desc = translations(content_type.name + "-none")
                if desc:
                    return desc
        
        return self._empty_label

    def _set_empty_label(self, value):
        self._empty_label = value

    empty_label = property(_get_empty_label, _set_empty_label)

    def _build(self):
    
        Element._build(self)

        self.add_resource("/resources/scripts/ItemSelector.js")        
        self.set_client_param("emptyLabel", self.empty_label)

        self.input = templates.new("cocktail.html.HiddenInput")
        self.append(self.input)
        self.binding_delegate = self.input

        self.button = Element("button", name = "rel", type="submit")
        self.append(self.button)

        self.selection_label = templates.new("sitebasis.views.ItemLabel")
        self.selection_label.tag = "span"
        self.selection_label.add_class("selection_label")
        self.button.append(self.selection_label)

    def _ready(self):

        Element._ready(self)

        if self.member:            

            if self.data_display:
                param_name = self.data_display.get_member_name(
                    self.member,
                    self.language
                )
            else:
                param_name = self.member.name
            
            self.button["value"] = \
                self.member.type.full_name + "-" + param_name

        if self.value is None:
            self.selection_label.add_class("empty_selection")
            self.selection_label.append(self.empty_label)
        else:        
            self.input["value"] = self.value.id
            self.selection_label.item = self.value

