#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			August 2009
"""
from cocktail.modeling import cached_getter
from cocktail import schema
from cocktail.controllers.userfilter import UserFilter, user_filters_registry
from sitebasis.models.item import Item
from sitebasis.models.document import Document
from sitebasis.models.resource import Resource
from sitebasis.models.expressions import DocumentIsPublishedExpression
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

