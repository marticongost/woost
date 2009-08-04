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
from sitebasis.models import (
    Item,
    Document,
    DocumentIsPublishedExpression,
    get_current_user
)


class OwnItemsFilter(UserFilter):

    id = "own-items"

    @cached_getter
    def schema(self):
        return schema.Schema()

    @cached_getter
    def expression(self):
        return Item.owner.equal(get_current_user())

Item.custom_user_filters = [OwnItemsFilter]


class PublishedDocumentsFilter(UserFilter):

    id = "published"

    @cached_getter
    def schema(self):
        return schema.Schema()

    @cached_getter
    def expression(self):
        return DocumentIsPublishedExpression(get_current_user())

Document.custom_user_filters = [PublishedDocumentsFilter]

