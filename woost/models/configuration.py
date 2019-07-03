"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from decimal import Decimal

from cocktail.modeling import classgetter
from cocktail.translations import (
    require_language,
    set_language,
    set_fallback_languages
)
from cocktail.persistence import datastore
from cocktail import schema

from woost import app
from .item import Item
from .website import Website

try:
    from fractions import Fraction
except ImportError:
    _numerical_types = (int, float, Decimal)
else:
    _numerical_types = (int, float, Decimal, Fraction)


class Configuration(Item):

    instantiable = False

    @classgetter
    def instance(cls):
        instance = datastore.get_transaction_value("woost.configuration")
        if instance is None:
            instance = cls.get_instance(qname="woost.configuration")
            datastore.set_transaction_value("woost.configuration", instance)
        return instance

    def setup_languages(self):
        set_language(self.default_language)
        for language, fallback_languages in self.fallback_languages:
            set_fallback_languages(language, fallback_languages)

    def get_setting(self, key):
        """Obtains the value for the indicated configuration option.

        The method will search the active website first (see
        L{woost.Application.website}), and the site's L{Configuration}
        if there is no active website, or if the website provides no
        significant value. Significant values include numbers, booleans, and
        any object that evaluates to True on a boolean context.

        @param key: The name of the value to obtain. Must match one of the
            members of the L{Configuration} or the L{Website} models.
        @type key: str

        @return: The value for the indicated configuration option.
        """
        website = app.website

        if website is not None:
            value = getattr(website, key, None)
            if self._is_significant_setting_value(key, value):
                return value

        return getattr(self.instance, key, None)

    def _is_significant_setting_value(self, key, value):
        return value or isinstance(value, _numerical_types)

    def language_is_enabled(self, language=None):
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

        return smtp

    def get_website_by_host(self, host):

        # Specific match
        for website in Website.select():
            if host in website.hosts:
                return website

        # Partial wildcards (ie. *.foo.com)
        while True:
            pos = host.find(".")

            if pos == -1:
                break

            host = host[pos + 1:]
            wildcard = "*." + host
            for website in Website.select():
                if wildcard in website.hosts:
                    return website

        # Generic wildcard (*)
        for website in Website.select():
            if "*" in website.hosts:
                return website

