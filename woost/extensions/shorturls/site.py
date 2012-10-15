#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Site
from woost.extensions.shorturls.urlshortener import URLShortener


Site.add_member(
    schema.Reference("url_shortener",
        type = URLShortener,
        related_end = schema.Reference(),
        member_group = "behavior.publication",
        after_member = "caching_policies"
    )
)

