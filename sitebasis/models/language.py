#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.modeling import classgetter
from cocktail.translations import translate
from cocktail import schema
from sitebasis.models.item import Item

class Language(Item):
 
    members_order = "iso_code", "fallback_languages"

    iso_code = schema.String(
        required = True,
        unique = True,
        max = 64
    )
    
    fallback_languages = schema.Collection(
        items = "sitebasis.models.Language"
    )

    @classgetter
    def codes(cls):
        return [language.iso_code for language in cls.select()]

    def __translate__(self, language, **kwargs):
        return self.iso_code and translate(self.iso_code) \
            or Item.__translate__(self, language, **kwargs)

