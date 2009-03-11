#-*- coding: utf-8 -*-
"""

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

    root_visible = False
    selection = None
    emphasized_selection = True
    linked_selection = True
    max_depth = None
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
        return is_accessible(item) and not item.hidden

    def get_item_uri(self, item):
        return self._cms.application_uri(item.full_path or "")

    def create_entry(self, item):
        entry = TreeView.create_entry(self, item)

        if item in self._expanded:
            entry.add_class("selected")

        return entry

    def create_label(self, item):

        item_uri = self.get_item_uri(item)
        item_content = TreeView.create_label(self, item)
        
        if item is self.selection \
        and (self.emphasized_selection or not self.linked_selection):
            
            label = Element("strong" if self.emphasized_selection else "span")
            
            if self.linked_selection:
                link = Element("a")
                link["href"] = item_uri
                link.append(item_content)
                label.append(link)
            else:
                label.append(item_content)
        else:
            label = Element("a")
            label["href"] = item_uri
            label.append(item_content)

        return label

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

