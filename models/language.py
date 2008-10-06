#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail import schema
from cocktail.persistence import Entity
from sitebasis.models import Item

class Language(Item):
 
    members_order = "title", "iso_code", "fallback_languages"

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        translated = True
    )

    iso_code = schema.String(
        required = True,
        unique = True,
        max = 64
    )
    
    fallback_languages = schema.Collection(
        items = "sitebasis.models.Language"
    )

    def __translate__(self, language, **kwargs):
        return self.get("title", language) \
            or Entity.__translate__(self, language, **kwargs)

