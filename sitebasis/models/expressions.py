#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
from datetime import datetime
from cocktail.schema.expressions import Expression
from sitebasis.models.action import Action
from sitebasis.models.usersession import get_current_user
from sitebasis.models.item import Item
from sitebasis.models.document import Document
from sitebasis.models.permission import ReadPermission


class PermissionExpression(Expression):
    """An schema expression that indicates if the specified user has permission
    over an element.
    """
    user = None
    permission_type = None

    def __init__(self, user, permission_type):
        self.user = user
        self.permission_type = permission_type

    def eval(self, context, accessor = None):
        return self.user.has_permission(self.permission_type, target = context)

    def resolve_filter(self, query):

        def impl(dataset):

            authorized_subset = set()
            queried_type = query.type

            for permission in reversed(list(
                self.user.iter_permissions(self.permission_type)
            )):
                permission_query = permission.select_items()

                if issubclass(queried_type, permission_query.type) \
                or issubclass(permission_query.type, queried_type):

                    permission_subset = permission_query.execute()

                    if permission.authorized:
                        authorized_subset.update(permission_subset)
                    else:
                        authorized_subset.difference_update(permission_subset)

            dataset.intersection_update(authorized_subset)
            return dataset

        return ((0, 0), impl)


class DocumentIsPublishedExpression(Expression):
    """An expression that tests if documents are published."""

    def eval(self, context, accessor = None):
        return context.is_published()

    def resolve_filter(self, query):

        def impl(dataset):

            is_draft_expr = Item.is_draft.equal(False)
            enabled_expr = Document.enabled.equal(True)

            dataset = is_draft_expr.resolve_filter(query)[1](dataset)
            dataset = enabled_expr.resolve_filter(query)[1](dataset)

            now = datetime.now()

            s = Document.start_date.index
            e = Document.end_date.index

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


class DocumentIsAccessibleExpression(Expression):
    """An expression that tests that documents can be accessed by a user.
    
    The expression checks both the publication state of the document and the
    read permissions for the specified user.

    @ivar user: The user that accesses the documents.
    @type user: L{User<sitebasis.models.user.User>}
    """

    def __init__(self, user = None):
        Expression.__init__(self)
        self.user = user

    def eval(self, context, accessor = None):
        return context.is_accessible(user = self.user)

    def resolve_filter(self, query):

        def impl(dataset):
            access_expr = PermissionExpression(
                self.user or get_current_user(),
                ReadPermission
            )
            published_expr = DocumentIsPublishedExpression()            
            dataset = access_expr.resolve_filter(query)[1](dataset)
            dataset = published_expr.resolve_filter(query)[1](dataset)
            return dataset
        
        return ((-1, 1), impl)

