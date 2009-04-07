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
from sitebasis.models import Item


class ContentDisplayMixin(object):

    base_url = None
    edit_stack = None
    authorization_check = None

    def __init__(self):

        @extend(self)
        def get_member_display(self, item, member):
            if self.authorization_check is not None \
            and not self.authorization_check(
                target_instance = item,
                target_member = member,
                language = get_content_language()
                    if member.translated else None,
                action = "read"
            ):
                sign = Element()
                sign.add_class("forbidden")
                sign.append(translate("forbidden value"))
                return sign
            else:
                return call_base(item, member)

        @extend(self)
        def _resolve_member_display(self, obj, member):

            if isinstance(member, Reference):
                if member.is_persistent_relation \
                and issubclass(member.type, Item):
                    return self.display_item_reference
            
            if isinstance(member, Collection):
                if member.is_persistent_relation \
                and issubclass(member.items.type, Item):
                    return self.display_item_collection

            return call_base(obj, member)

    def display_item_reference(self, obj, member):
        display = templates.new("sitebasis.views.ContentLink")
        display.item = self.get_member_value(obj, member)
        display.base_url = self.base_url
        display.edit_stack = self.edit_stack
        return display
    
    def display_item_collection(self, obj, member):
        display = templates.new("sitebasis.views.ContentList")
        display.authorization_check = self.authorization_check
        display.items = self.get_member_value(obj, member)
        display.base_url = self.base_url
        display.edit_stack = self.edit_stack
        return display

