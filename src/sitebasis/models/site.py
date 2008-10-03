#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.modeling import classgetter
from cocktail import schema
from cocktail.persistence import datastore
from sitebasis.models.item import Item


class Site(Item):

    indexed = True

    @classgetter
    def main(cls):
        return datastore.root["main_site"]

    default_language = schema.String(
        required = True,
        default = "en"
    )
    
    languages = schema.Collection(
        required = True,
        min = 1,
        items = schema.String,
        default = ["en"]
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

