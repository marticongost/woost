#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.modeling import extend, call_base
from cocktail.language import get_content_language
from cocktail.translations import translations
from cocktail.schema import Member, Reference, Collection
from cocktail.html import templates, Element
from sitebasis.models import (
    get_current_user,
    Item,
    ReadMemberPermission
)

# Extension property that allows members to define their appearence in several
# points of the application (listings, detail views, etc) from just one place
Member.display = None


class ContentDisplayMixin(object):

    base_url = None

    def __init__(self):

        @extend(self)
        def _resolve_member_display(self, obj, member):

            display = getattr(member, "display", None)
            
            if display is None:
                display = call_base(obj, member)

            return display

        @extend(self)
        def get_default_member_display(self, obj, member):

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
        display.referer = obj
        display.member = member
        return display
    
    def display_item_collection(self, obj, member):
        display = templates.new("sitebasis.views.ContentList")
        display.items = self.get_member_value(obj, member)
        display.base_url = self.base_url
        display.referer = obj
        display.member = member
        return display

