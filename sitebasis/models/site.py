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
from cocktail.persistence import datastore
from sitebasis.models.item import Item
from sitebasis.models.language import Language


class Site(Item):

    indexed = True
    instantiable = False

    members_order = [
        "default_language",
        "home",
        "generic_error_page",
        "not_found_error_page",
        "forbidden_error_page"
    ]

    @classgetter
    def main(cls):
        return cls.get_instance(qname = "sitebasis.main_site")

    default_language = schema.String(
        required = True,
        default = "en",
        enumeration = lambda ctx: Language.codes
    )
    
    home = schema.Reference(
        type = "sitebasis.models.Document",
        required = True
    )

    login_page = schema.Reference(
        type = "sitebasis.models.Document"
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

    access_rules_by_priority = schema.Collection(
        items = "sitebasis.models.AccessRule",
        bidirectional = True
    )

    plugins = schema.Collection(
        items = "sitebasis.models.PlugIn"
    )

    def __translate__(self, language, **kwargs):
        return translate(self.__class__.__name__, language, **kwargs)

