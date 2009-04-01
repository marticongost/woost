#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from cocktail.html import Element
from cocktail.html.databoundcontrol import DataBoundControl
from sitebasis.views.contenttypetree import ContentTypeTree


class ContentTypePicker(ContentTypeTree, DataBoundControl):
    
    name = None
    value = None

    empty_option_displayed = True
    empty_label = "---"
    empty_value = ""

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        DataBoundControl.__init__(self)

    def _build(self):
        ContentTypeTree._build(self)
        self.add_resource("/cocktail/scripts/jquery.js")
        self.add_resource("/resources/scripts/ContentTypePicker.js")

    def _ready(self):
        
        if self.member and self.name is None and self.member.name:
            self.name = self.member.name

        if self.empty_option_displayed:
            self.append(self.create_empty_option())

        ContentTypeTree._ready(self)

    def create_empty_option(self):
        
        entry = Element("li")

        entry.option = Element("input",
            type = "radio",
            name = self.name,
            value = self.empty_value,
            checked = self.value is None
        )
        self._bind_member(entry.option)
        entry.append(entry.option)

        entry.label = Element("label")
        entry.label.add_class("entry_label")
        entry.label.add_class("empty_option")
        entry.label.append(self.empty_label)
        entry.append(entry.label)

        entry.label["for"] = entry.option.require_id()

        return entry

    def create_entry(self, content_type):
        
        entry = ContentTypeTree.create_entry(self, content_type)        

        entry.option = Element("input",
            type = "radio",
            name = self.name,
            value = content_type.__name__,
            checked = content_type is self.value)

        self._bind_member(entry.option)
        entry.insert(0, entry.option)
        entry.label["for"] = entry.option.require_id()
        return entry

    def create_label(self, content_type):
        label = ContentTypeTree.create_label(self, content_type)
        label.tag = "label"
        return label

