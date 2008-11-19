#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.modeling import classgetter
from cocktail.translations import translate
from cocktail import schema
from cocktail.persistence import Entity
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
        return [language.iso_code for language in cls.index.itervalues()]

    def __translate__(self, language, **kwargs):
        return self.iso_code and translate(self.iso_code) \
            or Entity.__translate__(self, language, **kwargs)

