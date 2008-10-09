#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html import Element, templates
from sitebasis.models import Item

ContentTypeSelector = \
    templates.get_class("sitebasis.views.ContentTypeSelector")


class ContentTypePath(Element):
    
    tag = "ul"
    value = None

    Entry = Element
    Selector = ContentTypeSelector
    
    def _ready(self):
        
        inheritance_line = reversed(list(self.value.ascend_inheritance(True)))
        
        for content_type in inheritance_line:
            entry = self.create_entry(content_type)
            self.append(entry)

        self._last_entry = entry
        Element._ready(self)

    def _content_ready(self):

        Element._content_ready(self)

        for derived_content_type in self.value.derived_entities():
            break
        else:
            self._last_entry.selector.tree.visible = False
            self._last_entry.add_class("leaf")

    def create_entry(self, content_type):        
        entry = self.Entry()
        entry.tag = "li"
        entry.selector = self.create_selector(content_type)
        entry.append(entry.selector)        
        return entry

    def create_selector(self, content_type):
        selector = self.Selector()
        selector.root = content_type
        selector.value = content_type

        if content_type is self.value:
            selector.add_class("selected")
    
        return selector

