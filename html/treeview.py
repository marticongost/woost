#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet.html import Element

class TreeView(Element):

    tag = "ul"
    root = None

    def _ready(self):
        if self.root is not None:
            self.root_entry = self.create_entry(self.root)
            self.append(self.root_entry)

    def create_entry(self, item):
        
        entry = Element("li")
    
        entry.append(self.create_label(item))

        children = self.get_child_items(item)

        if children:
            container = self.create_children_container(item, children)
            entry.append(container)

        return entry

    def create_label(self, item):
        label = Element("div")
        label.add_class("entry_label")
        label.append(item.title)
        return label

    def create_children_container(self, item, children):
        
        container = Element("ul")
        
        for child in children:
            container.append(self.create_entry(child))

        return container

    def get_child_items(self, parent):
        return parent.children
        

