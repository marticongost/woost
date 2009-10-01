#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail import schema
from sitebasis.models import Item


class Country(Item):

    members_order = ["country_name", "iso_code"]

    country_name = schema.String(
        unique = True,
        required = True,
        indexed = True,
        normalized_index = True,
        translated = True
    )

    iso_code = schema.String(
        unique = True,
        required = True,
        indexed = True,
        format = "a-z{2}"
    )

    def __translate__(self, language, **kwargs):
        return (
            self.draft_source is None
            and self.get("country_name", language)
        ) or Item.__translate__(self, language, **kwargs)

