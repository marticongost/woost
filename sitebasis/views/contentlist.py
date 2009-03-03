#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.html import templates

List = templates.get_class("cocktail.html.List")


class ContentList(List):

    base_url = None
    authorization_check = None
    edit_stack = None

    def _fill_entries(self):
        items = self.items

        if self.authorization_check:
            items = [
                item
                for item in self.items
                if self.authorization_check(
                    target_instance = item,
                    action = "read"
                )
            ]

        if items:            
            List._fill_entries(self)
        else:
            self.append(u"-")

    def create_entry_content(self, item):
        link = templates.new("sitebasis.views.ContentLink")
        link.item = item
        link.base_url = self.base_url
        link.edit_stack = self.edit_stack
        return link

