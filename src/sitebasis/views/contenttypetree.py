#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			August 2008
"""
from cocktail.translations import translate
from cocktail.html import Element, TreeView
from sitebasis.models import Item


class ContentTypeTree(TreeView):

    root = Item
    root_visible = True
    plural_labels = False

    def create_label(self, content_type):
        
        label = Element()

        label.add_class("entry_label")

        for schema in content_type.descend_inheritance(True):
            label.add_class(schema.name)

        label.append(self.get_item_label(content_type))
        return label

    def get_item_label(self, content_type):
        if self.plural_labels:
            return translate(content_type.__name__ + "-plural")
        else:
            return translate(content_type.__name__)

    def get_child_items(self, content_type):
        return sorted(
            content_type.derived_entities(recursive = False),
            key = lambda ct: translate(ct.__name__))


class ContentTypeSelector(Element):

    value = None
    Tree = ContentTypeTree
    root = Item
    root_visible = True

    def _build(self):
        self.add_class("selector")

    def _ready(self):        
        
        self.tree = self.create_tree()
        self.label = self.create_label()

        self.append(self.label)
        self.append(self.tree)

        Element._ready(self)

    def create_label(self):
        label = self.tree.create_label(self.value)
        label.tag = "span"
        label.add_class("label")
        return label

    def create_tree(self):
        tree = self.Tree()
        tree.add_class("selector_content")
        tree.root = self.root
        tree.root_visible = self.root_visible
        return tree


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

