#-*- coding: utf-8 -*-
u"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from cocktail.html import templates, Element
from cocktail.controllers import context
from sitebasis.models import Site
from sitebasis.controllers import is_accessible

TreeView = templates.get_class("cocktail.html.TreeView")


class Menu(TreeView):
    """A visual component used to render navigation menus and site maps."""

    # To Show/Hide Root Node
    root_visible = False

    # To specify the selected item, document by default
    selection = None

    # To Add strong tag on selected item
    emphasized_selection = True

    # To enable/disable link for selected item
    linked_selection = True

    # To enable/disable link for each container node
    linked_containers = True

    # To set a max depth for the menu, no limit by default
    max_depth = None

    # To enable/disable auto expand each container node
    expanded = False

    def _ready(self):

        self._cms = context["cms"]

        # Set the menu root to the site's home page
        if self.root is None:
            self.root = Site.main.home

        # Set the selected document from the current context
        if self.selection is None:
            self.selection = context["document"]
        
        # Find the selected path
        self._expanded = set()
        item = self.selection

        while item is not None:
            self._expanded.add(item)
            item = item.parent

        # Limited depth
        self._depth = 2 if self.root_visible else 1

        TreeView._ready(self)
    
    def filter_item(self, item):
        return not item.hidden and item.is_accessible()

    def get_item_uri(self, item):
        return self._cms.canonical_uri(item)

    def create_entry(self, item):
        entry = TreeView.create_entry(self, item)

        if item in self._expanded:
            entry.add_class("selected")

        return entry

    def create_label(self, item):
        
        if self.should_link(item):
            label = Element("a")
            label["href"] = self.get_item_uri(item)
        else:
            label = Element("span")
        
        label.append(self.get_item_label(item))

        if self.emphasized_selection and item is self.selection:
            if label.tag == "a":
                label = Element("strong", children = [label])
            else:
                label.tag = "strong"

        return label

    def should_link(self, item):
        return (self.linked_selection or item is not self.selection) \
            and (self.linked_containers or not item.children)

    def get_child_items(self, parent):

        if (self.max_depth is not None and self._depth > self.max_depth) \
        or (not self.expanded and parent not in self._expanded):
            return []
        else:
            return TreeView.get_child_items(self, parent)

    def _fill_children_container(self, container, item, children):
        self._depth += 1
        TreeView._fill_children_container(self, container, item, children)
        self._depth -= 1        

