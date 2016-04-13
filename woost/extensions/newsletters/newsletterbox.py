#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Block, Slot


class NewsletterBox(Block):

    type_group = "blocks.newsletter"
    default_view_class = "woost.extensions.newsletters.NewsletterBoxView"
    views = ["woost.extensions.newsletters.NewsletterBoxView"]

    members_order = [
        "blocks"
    ]

    blocks = Slot()

