#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from cocktail import schema
from woost.models import Slot
from woost.extensions.newsletters.members import NewsletterContentAppearence
from woost.extensions.newsletters.newslettercontainer \
    import NewsletterContainer


class NewsletterBox(NewsletterContainer):

    members_order = [
        "view_class",
        "blocks",
        "content_appearence"
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

    blocks = Slot()

    content_appearence = NewsletterContentAppearence(
        member_group = "content.entries"
    )

    def init_view(self, view):
        NewsletterContainer.init_view(self, view)
        view.container = self
        view.slot = "blocks"
        view.content_appearence = self.content_appearence

