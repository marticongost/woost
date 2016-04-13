#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Block, Publishable


class NewsletterListing(Block):

    type_group = "blocks.newsletter"
    default_view_class = "woost.extensions.newsletters.NewsletterListingTextOnlyView",
    views = [
        "woost.extensions.newsletters.NewsletterListingTextOnlyView",
        "woost.extensions.newsletters.NewsletterListingTextAndIconView",
        "woost.extensions.newsletters.NewsletterListingSummaryView"
    ]

    members_order = [
        "listed_items"
    ]

    listed_items = schema.Collection(
        items = schema.Reference(type = Publishable),
        related_end = schema.Collection(),
        member_group = "content"
    )

    def init_view(self, view):
        Block.init_view(self, view)
        view.listed_items = self.listed_items

