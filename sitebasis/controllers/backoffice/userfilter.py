#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
from cocktail.modeling import cached_getter
from cocktail import schema
from cocktail.controllers import context
from cocktail.controllers.userfilter import UserFilter
from sitebasis.models import Item, Document, DocumentIsAccessibleExpression


class OwnItemsFilter(UserFilter):

    id = "own-items"

    @cached_getter
    def schema(self):
        return schema.Schema()

    @cached_getter
    def expression(self):
        return Item.owner.equal(context["cms"].user)


Item.custom_user_filters = [OwnItemsFilter]


class PublishedDocumentsFilter(UserFilter):

    id = "published"

    @cached_getter
    def schema(self):
        return schema.Schema()

    @cached_getter
    def expression(self):
        return DocumentIsAccessibleExpression(context["cms"].user)

Document.custom_user_filters = [PublishedDocumentsFilter]


