#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from cocktail.html import Element, AutoID
from sitebasis.views.contenttypetree import ContentTypeTree


class ContentTypePicker(ContentTypeTree):
    
    name = None
    value = None

    empty_option_displayed = True
    empty_label = "---"
    empty_value = ""

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
        option_id = AutoID()

        entry.option = Element("input",
            type = "radio",
            name = self.name,
            id = option_id,
            value = self.empty_value,
            checked = self.value is None
        )
        entry.append(entry.option)

        entry.label = Element("label")
        entry.label.add_class("entry_label")
        entry.label.add_class("empty_option")
        entry.label["for"] = option_id
        entry.label.append(self.empty_label)
        entry.append(entry.label)

        return entry

    def create_entry(self, content_type):
        
        entry = ContentTypeTree.create_entry(self, content_type)        
        option_id = AutoID()
        entry.label["for"] = option_id

        entry.option = Element("input",
            type = "radio",
            name = self.name,
            id = option_id,
            value = content_type.__name__,
            checked = content_type is self.value)

        entry.insert(0, entry.option)
        return entry

    def create_label(self, content_type):
        label = ContentTypeTree.create_label(self, content_type)
        label.tag = "label"
        return label

