#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.modeling import classgetter
from cocktail.translations import translations
from cocktail import schema
from cocktail.persistence import datastore
from sitebasis.models.item import Item
from sitebasis.models.language import Language
from sitebasis.models.file import File


class Site(Item):

    indexed = True
    instantiable = False

    members_order = [
        "default_language",
        "home",
        "login_page",
        "generic_error_page",
        "not_found_error_page",
        "forbidden_error_page",
        "icon",
        "keywords",
        "description",
        "smtp_host",
        "triggers"
    ]

    @classgetter
    def main(cls):
        return cls.get_instance(qname = "sitebasis.main_site")

    default_language = schema.String(
        required = True,
        default = "en",
        enumeration = lambda ctx: Language.codes,
        listed_by_default = False,
        translate_value = lambda value, **kwargs:
            u"" if not value else translations(value, **kwargs)
    )
    
    home = schema.Reference(
        type = "sitebasis.models.Document",
        required = True,
        listed_by_default = False
    )

    login_page = schema.Reference(
        type = "sitebasis.models.Document",
        listed_by_default = False
    )

    generic_error_page = schema.Reference(
        type = "sitebasis.models.Document",
        listed_by_default = False
    )

    not_found_error_page = schema.Reference(
        type = "sitebasis.models.Document",
        listed_by_default = False
    )

    forbidden_error_page = schema.Reference(
        type = "sitebasis.models.Document",
        listed_by_default = False
    )

    icon = schema.Reference(
        type = File,
        relation_constraints = [File.resource_type.equal("image")],
        related_end = schema.Collection(),
        listed_by_default = False
    )

    keywords = schema.String(
        translated = True,
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea"
    )

    description = schema.String(
        translated = True,
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea"
    )

    smtp_host = schema.String(
        default = "localhost",
        listed_by_default = False
    )

    triggers = schema.Collection(
        items = "sitebasis.models.Trigger",
        bidirectional = True
    )

    def __translate__(self, language, **kwargs):
        return translations(self.__class__.__name__, language, **kwargs)

