#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import re
from cocktail.modeling import classgetter
from cocktail.translations import translations
from cocktail import schema
from cocktail.persistence import datastore
from woost.models.item import Item
from woost.models.language import Language
from woost.models.file import File
from woost.models.publicationschemes import PathResolution


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
        "publication_schemes",
        "triggers"
    ]

    @classgetter
    def main(cls):
        return cls.get_instance(qname = "woost.main_site")

    default_language = schema.String(
        required = True,
        default = "en",
        enumeration = lambda ctx: Language.codes,
        listed_by_default = False,
        translate_value = lambda value, **kwargs:
            u"" if not value else translations(value, **kwargs)
    )
    
    home = schema.Reference(
        type = "woost.models.Publishable",
        required = True,
        listed_by_default = False
    )

    login_page = schema.Reference(
        type = "woost.models.Publishable",
        listed_by_default = False
    )

    generic_error_page = schema.Reference(
        type = "woost.models.Publishable",
        listed_by_default = False
    )

    not_found_error_page = schema.Reference(
        type = "woost.models.Publishable",
        listed_by_default = False
    )

    forbidden_error_page = schema.Reference(
        type = "woost.models.Publishable",
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
        items = "woost.models.Trigger",
        bidirectional = True
    )

    timezone = schema.String(
        required = False,
        format = re.compile(r'^["GMT"|"UTC"|"PST"|"MST"|"CST"|"EST"]{3}$|^[+-]\d{4}$')
    )

    publication_schemes = schema.Collection(
        items = "woost.models.PublicationScheme",
        bidirectional = True,
        integral = True,
        min = 1
    )

    def __translate__(self, language, **kwargs):
        return translations(self.__class__.__name__, language, **kwargs)
    
    def resolve_path(self, path):
        """Determines the publishable item that matches the indicated path.

        This method identifies a matching publishable item by trying each
        publication scheme defined by the site, in order. Once a scheme finds a
        matching item, the search concludes.
        
        See L{PublicationScheme.resolve_path} for more details on the resolution
        process.
 
        @param path: The path to evaluate; A list-like object describing a
            a path relative to the application's root.
        @type path: str list

        @return: A structure containing the matching item and its publication
            details. If no matching item can be found, None is returned
            instead.
        @rtype: L{PathResolution}
        """
        if not path:
            return PathResolution(None, self.home)
        else:
            for pubscheme in self.publication_schemes:
                resolution = pubscheme.resolve_path(path)
                if resolution is not None:
                    return resolution

    def get_path(self, publishable, language = None):
        """Determines the canonical path of the indicated item.
        
        This method queries each publication scheme defined by the site, in
        order. Once a scheme yields a matching path, the search concludes. That
        first match will be considered the item's canonical path.

        See L{PublicationScheme.get_path} for more details on how paths for
        publishable items are determined.

        @param publishable: The item to get the canonical path for.
        @type publishable: L{Publishable<woost.models.publishable.Publishable>}

        @param language: The language to get the path in (some schemes produce
            different canonical paths for the same content in different
            languages).
        @type language: str

        @return: The publication path for the indicated item, relative to the
            application's root. If none of the site's publication schemes can
            produce a suitable path for the item, None is returned instead.
        @rtype: unicode
        """
        # The path to the home page is always the application root
        if publishable is self.home:
            return ""

        for pubscheme in self.publication_schemes:
            path = pubscheme.get_path(publishable, language)
            if path is not None:
                return path

