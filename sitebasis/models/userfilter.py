#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			August 2009
"""
from cocktail.modeling import cached_getter
from cocktail.schema.expressions import (
    Self,
    InclusionExpression,
    ExclusionExpression
)
from cocktail import schema
from cocktail.html import templates
from cocktail.html.datadisplay import MULTIPLE_SELECTION
from cocktail.controllers.userfilter import UserFilter, user_filters_registry
from sitebasis.models.item import Item
from sitebasis.models.document import Document, DocumentIsPublishedExpression
from sitebasis.models.resource import Resource
from sitebasis.models.usersession import get_current_user


class OwnItemsFilter(UserFilter):

    id = "owned-items"

    @cached_getter
    def schema(self):
        return schema.Schema()

    @cached_getter
    def expression(self):
        return Item.owner.equal(get_current_user())

user_filters_registry.add(Item, OwnItemsFilter)


class PublishedDocumentsFilter(UserFilter):

    id = "published"

    @cached_getter
    def schema(self):
        return schema.Schema()

    @cached_getter
    def expression(self):
        return DocumentIsPublishedExpression(get_current_user())

user_filters_registry.add(Document, PublishedDocumentsFilter)
user_filters_registry.add(Resource, PublishedDocumentsFilter)


class TypeFilter(UserFilter):
    id = "type"
    operators = ["eq", "ne"]

    @cached_getter
    def schema(self):
        
        def types_search_control(parent, obj, member):
            selector = templates.new("sitebasis.views.ContentTypePicker")
            selector.root = self.content_type
            selector.selection_mode = MULTIPLE_SELECTION
            return selector

        return schema.Schema("UserFilter", members = [
            schema.String(
                "operator",
                required = True,
                enumeration = self.operators
            ),
            schema.Collection(
                "types",
                items = schema.Reference("item_type", class_family = Item),
                search_control = types_search_control
            ),
            schema.Boolean(
                "is_inherited"
            )
        ])

    @cached_getter
    def expression(self):

        ids = set()

        for cls in self.types:
            if self.is_inherited:
                ids.update(cls.keys)
            else:
                children = cls.derived_schemas(recursive = False)
                children_ids = set()
                for child in children:
                    children_ids.update(child.keys)
                ids.update(set(cls.keys).difference(children_ids))

        print ids
        if self.operator == "eq":
            expr = InclusionExpression(Self, ids)
        elif self.operator == "ne":
            expr = ExclusionExpression(Self, ids)

        expr.by_key = True
        return expr

user_filters_registry.add(Item, TypeFilter)

