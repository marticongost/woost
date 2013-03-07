#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Configuration
from woost.extensions.shorturls.urlshortener import URLShortener


Configuration.add_member(
    schema.Reference("url_shortener",
        type = URLShortener,
        related_end = schema.Reference(),
        member_group = "behavior.publication",
        after_member = "caching_policies",
        listed_by_default = False
    )
)

