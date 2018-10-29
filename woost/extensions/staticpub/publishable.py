#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models import Publishable, URI

translations.load_bundle("woost.extensions.staticpub.publishable")

Publishable.add_member(
    schema.Boolean(
        "included_in_static_publication",
        required = True,
        default = True,
        indexed = True,
        affects_cache_invalidation = False,
        listed_by_default = False,
        member_group = "publication"
    )
)

URI.default_included_in_static_publication = False

