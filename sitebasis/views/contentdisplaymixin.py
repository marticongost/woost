#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.modeling import extend, call_base
from cocktail.language import get_content_language
from cocktail.translations import translate
from cocktail.schema import Reference, Collection
from cocktail.html import templates, Element


class ContentDisplayMixin(object):

    base_url = None
    edit_stack = None
    authorization_check = None

    def __init__(self):
        self.set_member_type_display(Reference, self.display_reference)
        self.set_member_type_display(Collection, self.display_collection)

        @extend(self)
        def get_member_display(self, item, column):
            if self.authorization_check is not None \
            and not self.authorization_check(
                target_instance = item,
                target_member = column,
                language = get_content_language()
                    if column.translated else None,
                action = "read"
            ):
                sign = Element()
                sign.add_class("forbidden")
                sign.append(translate("forbidden value"))
                return sign
            else:
                return call_base(item, column)

    def display_reference(self, obj, member):
        display = templates.new("sitebasis.views.ContentLink")
        display.item = self.get_member_value(obj, member)
        display.base_url = self.base_url
        display.edit_stack = self.edit_stack
        return display
    
    def display_collection(self, obj, member):
        display = templates.new("sitebasis.views.ContentList")
        display.authorization_check = self.authorization_check
        display.items = self.get_member_value(obj, member)
        display.base_url = self.base_url
        display.edit_stack = self.edit_stack
        return display

