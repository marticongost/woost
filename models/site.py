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
from cocktail.persistence import datastore
from sitebasis.models.item import Item
from sitebasis.models.language import Language


class Site(Item):

    indexed = True
    members_order = [
        "default_language",
        "home",
        "generic_error_page",
        "not_found_error_page",
        "forbidden_error_page"
    ]

    @classgetter
    def main(cls):
        return datastore.root["main_site"]

    default_language = schema.String(
        required = True,
        default = "en"
    )
    
    home = schema.Reference(
        type = "sitebasis.models.Document",
        required = True
    )

    not_found_error_page = schema.Reference(
        type = "sitebasis.models.Document"
    )

    forbidden_error_page = schema.Reference(
        type = "sitebasis.models.Document"
    )
    
    generic_error_page = schema.Reference(
        type = "sitebasis.models.Document"
    )

    def __translate__(self, language, **kwargs):
        return translate(self.__class__.__name__, language, **kwargs)

