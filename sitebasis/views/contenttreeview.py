#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
from cocktail.html import templates

TreeView = templates.get_class("cocktail.html.TreeView")


class ContentTreeView(TreeView):

    authorization_check = None
    base_url = None
    edit_stack = None

    def filter(self, item):
        if self.authorization_check:
            return self.authorization_check(target_instance = item)

    def create_label(self, item):
        label = templates.new("sitebasis.views.ContentLink")
        label.base_url = self.base_url
        label.item = item
        label.edit_stack = self.edit_stack
        return label

