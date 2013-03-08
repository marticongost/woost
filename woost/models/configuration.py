#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import re
from decimal import Decimal
from cocktail.modeling import classgetter
from cocktail.translations import translations, require_language
from cocktail import schema
from woost.models.item import Item
from woost.models.publishable import Publishable
from woost.models.website import Website
from woost.models.websitesession import get_current_website
from woost.models.publicationschemes import PublicationScheme, PathResolution
from woost.models.caching import CachingPolicy
from woost.models.rendering.renderer import Renderer
from woost.models.rendering.imagefactory import ImageFactory
from woost.models.trigger import Trigger

try:
    from fractions import Fraction
except ImportError:
    _numerical_types = (int, float, Decimal)
else:
    _numerical_types = (int, float, Decimal, Fraction)


class Configuration(Item):

    instantiable = False

    groups_order = [
        "publication",
        "publication.pages",
        "publication.maintenance",
        "language",
        "rendering",
        "system",
        "system.smtp",
        "admin"
    ]

    members_order = [
        "websites",
        "publication_schemes",
        "caching_policies",
        "down_for_maintenance",
        "maintenance_page",
        "maintenance_addresses",
        "login_page",
        "generic_error_page",
        "not_found_error_page",
        "forbidden_error_page",
        "languages",
        "published_languages",
        "default_language",
        "heed_client_language",
        "backoffice_language",
        "renderers",
        "image_factories",
        "timezone",
        "smtp_host",
        "smtp_user",
        "smtp_password",
        "triggers"
    ]

    @classgetter
    def instance(cls):
        return cls.get_instance(qname = "woost.configuration")

    # publication
    #--------------------------------------------------------------------------
    websites = schema.Collection(
        items = schema.Reference(type = Website),
        related_end = schema.Collection(),
        integral = True,
        member_group = "publication"
    )

    publication_schemes = schema.Collection(
        items = schema.Reference(type = PublicationScheme),
        integral = True,
        related_end = schema.Reference(),
        min = 1,
        member_group = "publication"
    )

    caching_policies = schema.Collection(
        items = schema.Reference(type = CachingPolicy),        
        integral = True,
        related_end = schema.Reference(),
        member_group = "publication"
    )
    
    login_page = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        listed_by_default = False,
        member_group = "publication.pages"
    )

    generic_error_page = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        listed_by_default = False,
        member_group = "publication.pages"
    )

    not_found_error_page = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        listed_by_default = False,
        member_group = "publication.pages"
    )

    forbidden_error_page = schema.Reference(
        type = Publishable,
        related_end = schema.Collection(),
        listed_by_default = False,
        member_group = "publication.pages"
    )
    
    down_for_maintenance = schema.Boolean(
        required = True,
        default = False,
        listed_by_default = False,
        member_group = "publication.maintenance"
    )

    maintenance_page = schema.Reference(
        type = "woost.models.Publishable",
        listed_by_default = False,
        member_group = "publication.maintenance"
    )

    maintenance_addresses = schema.Collection(
        items = schema.String(),
        listed_by_default = False,
        member_group = "publication.maintenance"
    )

    # language
    #------------------------------------------------------------------------------
    languages = schema.Collection(
        items = schema.String(
            format = "^[a-z]{2}$"
        ),
        min = 1,
        listed_by_default = False,
        member_group = "language"
    )
    
    published_languages = schema.Collection(
        items = schema.String(
            enumeration = languages,
            edit_control = "cocktail.html.TextBox"
        ),
        listed_by_default = False,
        member_group = "language"
    )

    default_language = schema.String(
        required = True,
        enumeration = languages,
        edit_control = "cocktail.html.TextBox",
        text_search = False,
        listed_by_default = False,
        member_group = "language"
    )

    heed_client_language = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "language"
    )

    backoffice_language = schema.String(
        required = True,
        enumeration = ["en", "es", "ca"],        
        default = "en",
        text_search = False,
        translate_value = lambda value, language = None, **kwargs:
            u"" if not value else translations(value, language, **kwargs),
        listed_by_default = False,
        member_group = "language"
    )

    # rendering
    #--------------------------------------------------------------------------     
    renderers = schema.Collection(
        items = schema.Reference(type = Renderer),
        bidirectional = True,
        integral = True,
        related_end = schema.Reference(),
        member_group = "rendering"
    )

    image_factories = schema.Collection(
        items = schema.Reference(type = ImageFactory),
        bidirectional = True,
        integral = True,
        related_end = schema.Reference(),
        member_group = "rendering"
    )

    # system
    #--------------------------------------------------------------------------
    timezone = schema.String(
        required = False,
        format = re.compile(r'^["GMT"|"UTC"|"PST"|"MST"|"CST"|"EST"]{3}$|^[+-]\d{4}$'),
        text_search = False,
        member_group = "system",
        listed_by_default = False
    )

    smtp_host = schema.String(
        default = "localhost",
        listed_by_default = False,
        text_search = False,
        member_group = "system.smtp"
    )

    smtp_user = schema.String(
        listed_by_default = False,
        text_search = False,
        member_group = "system.smtp"
    )

    smtp_password = schema.String(
        listed_by_default = False,
        text_search = False,
        member_group = "system.smtp"
    )

    # administration
    #--------------------------------------------------------------------------         
    triggers = schema.Collection(
        items = schema.Reference(type = Trigger),
        related_end = schema.Reference(),
        integral = True,
        member_group = "administration"
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
            website = get_current_website()
            if website:
                return PathResolution(None, website.home)
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
        if publishable.is_home_page():
            return ""

        for pubscheme in self.publication_schemes:
            path = pubscheme.get_path(publishable, language)
            if path is not None:
                return path

    def get_setting(self, key):
        """Obtains the value for the indicated configuration option.

        The method will search the active website first (see
        L{woost.models.get_current_website}), and the site's L{Configuration}
        if there is no active website, or if the website provides no
        significant value. Significant values include numbers, booleans, and
        any object that evaluates to True on a boolean context.

        @param key: The name of the value to obtain. Must match one of the
            members of the L{Configuration} or the L{Website} models.
        @type key: str

        @return: The value for the indicated configuration option.
        """
        website = get_current_website()

        if website is not None:
            value = getattr(website, key, None)
            if self._is_significant_setting_value(key, value):
                return value
        
        return getattr(self.instance, key, None)

    def _is_significant_setting_value(self, key, value):
        return value or isinstance(value, _numerical_types)

    def language_is_enabled(self, language = None):
        language_subset = self.get_setting("published_languages")
        if not language_subset:
            return True
        else:
            return require_language(language) in language_subset

    def get_enabled_languages(self):
        return self.get_setting("published_languages") or self.languages

    def connect_to_smtp(self):

        import smtplib
        smtp = smtplib.SMTP(self.get_setting("smtp_host"), smtplib.SMTP_PORT)

        user = self.get_setting("smtp_user")
        password = self.get_setting("smtp_password")

        if user and password:
            smtp.login(str(user), str(password))

        return user, password

    def get_website_by_host(self, host):

        # Specific match
        for website in self.websites:
            if host in website.hosts:
                return website

        # Partial wildcards (ie. *.foo.com)
        while True:
            pos = host.find(".")

            if pos == -1:
                break

            host = host[pos + 1:]
            wildcard = "*." + host
            for website in self.websites:
                if wildcard in website.hosts:
                    return website

        # Generic wildcard (*)
        for website in self.websites:
            if "*" in website.hosts:
                return website

