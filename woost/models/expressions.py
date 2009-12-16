#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from datetime import datetime
from cocktail.schema.expressions import Expression
from woost.models.item import Item
from woost.models.usersession import get_current_user
from woost.models.permission import ReadPermission, PermissionExpression


class IsPublishedExpression(Expression):
    """An expression that tests if items are published."""

    content_type = None

    def eval(self, context, accessor = None):
        return context.is_published()

    def resolve_filter(self, query):

        if self.content_type is None:
            raise ValueError("Content type is missing")

        def impl(dataset):

            is_draft_expr = Item.is_draft.equal(False)
            enabled_expr = self.content_type.enabled.equal(True)

            dataset = is_draft_expr.resolve_filter(query)[1](dataset)
            dataset = enabled_expr.resolve_filter(query)[1](dataset)

            now = datetime.now()

            s = self.content_type.start_date.index
            e = self.content_type.end_date.index

            # No start date set, or the start date has been reached
            dataset.intersection_update(
                s[None] | set(s.values(max = now))
            )
            
            # No end date set, or the end date hasn't been reached yet
            dataset.intersection_update(
                e[None] | set(e.values(min = now, excludemin = True))
            )

            return dataset
        
        return ((-1, 1), impl)


class IsAccessibleExpression(Expression):
    """An expression that tests that items can be accessed by a user.
    
    The expression checks both the publication state of the item and the
    read permissions for the specified user.

    @ivar user: The user that accesses the items.
    @type user: L{User<woost.models.user.User>}
    """
    content_type = None

    def __init__(self, user = None):
        Expression.__init__(self)
        self.user = user

    def eval(self, context, accessor = None):
        return context.is_accessible(user = self.user)

    def resolve_filter(self, query):

        if self.content_type is None:
            raise ValueError("Content type is missing")

        def impl(dataset):
            access_expr = PermissionExpression(
                self.user or get_current_user(),
                ReadPermission
            )
            published_expr = IsPublishedExpression()
            published_expr.content_type = self.content_type
            dataset = access_expr.resolve_filter(query)[1](dataset)
            dataset = published_expr.resolve_filter(query)[1](dataset)
            return dataset
        
        return ((-1, 1), impl)

