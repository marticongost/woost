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
from sitebasis.models.item import Item
from sitebasis.models.document import Document
from sitebasis.models.accessrule import allowed


class AccessAllowedExpression(Expression):
    """An expression that filters queried items according to the active access
    rules.
    """

    def __init__(self, user):
        self.user = user

    def eval(self, context, accessor = None):
        return allowed(
            user = self.user,
            target_instance = context,
            action = Action.get_instance(identifier = "read")
        )


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
    """An expression that tests that documents can be accessed by an agent.
    
    The expression checks both the publication state of the document and the
    read privileges for the specified agent.

    @ivar agent: The agent that accesses the documents.
    @type agent: L{Agent<sitebasis.models.agent.Agent>}
    """

    def __init__(self, agent):
        Expression.__init__(self)
        self.agent = agent

    def eval(self, context, accessor = None):
        return context.is_published() \
            and allowed(
                user = self.agent,
                action = "read",
                target_instance = context
            )

    def resolve_filter(self, query):

        def impl(dataset):
            access_expr = AccessAllowedExpression(self.agent)
            published_expr = DocumentIsPublishedExpression()            
            dataset = access_expr.resolve_filter(query)[1](dataset)
            dataset = published_expr.resolve_filter(query)[1](dataset)
            return dataset
        
        return ((-1, 1), impl)

