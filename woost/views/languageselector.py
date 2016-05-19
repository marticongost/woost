#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.translations import translations, get_language
from cocktail.html.element import Element
from cocktail.html import templates
from cocktail.html.utils import rendering_xml
from cocktail.controllers import context
from woost import app
from woost.models import (
    Configuration,
    ReadTranslationPermission
)

LinkSelector = templates.get_class("cocktail.html.LinkSelector")


class LanguageSelector(LinkSelector):

    tag = "ul"
    translated_labels = True
    missing_translations = "redirect" # "redirect", "hide", "disable"
    autohide = True

    def create_entry(self, item):

        entry = Element("li")
        link = self.create_entry_link(item)

        if self.is_selected(item):
            strong = Element("strong")
            strong.append(link)
            entry.append(strong)
        else:
            entry.append(link)

        if self.missing_translations != "redirect":
            publishable = app.publishable
            value = self.get_item_value(item)
            if not publishable.is_accessible(language = value):
                if self.missing_translations == "hide":
                    entry.visible = False
                elif self.missing_translations == "disable":
                    link.tag = "span"
                    link["href"] = None

        return entry

    def get_languages(self):
        config = Configuration.instance
        user = app.user
        return [
            language
            for language in (
                config.get_setting("published_languages")
                or config.languages
            )
            if user.has_permission(
                ReadTranslationPermission,
                language = language
            )
        ]

    def _ready(self):

        if self.items is None:
            self.items = self.get_languages()

        if self.value is None:
            self.value = get_language()

        if self.autohide and len(self.items) < 2:
            self.visible = False
        else:
            LinkSelector._ready(self)

            # Hack for IE <= 6
            if self.children:
                self.children[-1].add_class("last")

    def get_item_label(self, language):
        if self.translated_labels:
            return translations("locale", locale = language, language = language)
        else:
            return translations("locale", locale = language)

    def get_entry_url(self, language):
        cms = context["cms"]
        publishable = app.publishable

        if self.missing_translations == "redirect" \
        and not publishable.is_accessible(language = language):
            path = "/"
        else:
            path = None

        return cms.translate_uri(path = path, language = language)

    def create_entry_link(self, item):
        link = LinkSelector.create_entry_link(self, item)
        value = self.get_item_value(item)
        link["lang"] = value
        link["hreflang"] = value

        @link.when_ready
        def set_xml_lang():
            if rendering_xml():
                link["xml:lang"] = value

        return link

