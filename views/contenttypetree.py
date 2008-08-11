#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			August 2008
"""
from magicbullet.html import Element
from magicbullet.html.treeview import TreeView
from magicbullet.models import Item


class ContentTypeTree(TreeView):

    root = Item
    root_visible = False

    def create_label(self, content_type):
        
        label = Element()

        label.add_class("entry_label")

        for schema in content_type.descend_inheritance(True):
            label.add_class(schema.name)

        label.append(content_type.__name__)
        return label

    def get_child_items(self, content_type):
        return sorted(
            content_type.derived_entities(recursive = False),
            key = lambda ct: ct.__name__)

