#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			August 2008
"""
from cocktail.translations import translate
from cocktail.html import Element, templates
from sitebasis.models import Item

TreeView = templates.get_class("cocktail.html.TreeView")


class ContentTypeTree(TreeView):

    root = Item
    root_visible = True
    plural_labels = False

    def create_label(self, content_type):
        
        label = TreeView.create_label(self, content_type)

        for schema in content_type.descend_inheritance(True):
            label.add_class(schema.name)

        return label

    def get_item_label(self, content_type):
        if self.plural_labels:
            return translate(content_type.__name__ + "-plural")
        else:
            return translate(content_type.__name__)

    def get_child_items(self, content_type):
        return sorted(
            content_type.derived_schemas(recursive = False),
            key = lambda ct: translate(ct.__name__)
        )

    def filter_item(self, content_type):
        return content_type.visible


