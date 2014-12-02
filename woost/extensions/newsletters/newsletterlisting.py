#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Publishable, File
from woost.extensions.newsletters.viewfactories import view_factories
from woost.extensions.newsletters.newslettercontainer \
    import NewsletterContainer


class NewsletterListing(NewsletterContainer):

    members_order = [
        "view_class",
        "listed_items",
        "content_view_factory"
    ]

    view_class = schema.String(
        shadows_attribute = True,
        required = True,
        default = "woost.extensions.newsletters.NewsletterContainerView",
        enumeration = [
            "woost.extensions.newsletters.NewsletterContainerView"
        ],
        edit_control = "cocktail.html.RadioSelector",
        member_group = "content"
    )

    listed_items = schema.Collection(
        items = schema.Reference(type = Publishable),
        selector_default_type = File,
        related_end = schema.Collection(),
        member_group = "content"
    )

    content_view_factory = schema.String(
        required = True,
        default = "text",
        enumeration = [
            "text",
            "image",
            "text_and_image",
            "detail"
        ],
        member_group = "content.entries"
    )

    def init_view(self, view):
        NewsletterContainer.init_view(self, view)
        view.add_class(self.content_view_factory + "_view")
        view.items = self.listed_items
        view.content_view_factory = view_factories[self.content_view_factory]

