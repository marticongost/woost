#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
from decimal import Decimal
from cocktail.translations import translations
from cocktail import schema
from woost.models import Publishable

Publishable.add_member(
    schema.Boolean(
        "sitemap_indexable",
        required = True,
        default = True,
        indexed = True
    ),
    append = True
)

Publishable.add_member(
    schema.String("sitemap_change_frequency",
        enumeration = [
            "always",
            "hourly",
            "daily",
            "weekly",
            "monthly",
            "yearly",
            "never"
        ],
        translate_value = lambda value, language = None, **kwargs:
            "" if not value 
            else translations(
                "woost.extensions.sitemap.change_frequency " + value,
                language,
                **kwargs
            ),
        member_group = "sitemap"
    ),
    append = True
)

Publishable.add_member(
    schema.Decimal("sitemap_priority",
        default = Decimal("0.5"),
        min = 0,
        max = 1,
        member_group = "sitemap"
    ),
    append = True
)

