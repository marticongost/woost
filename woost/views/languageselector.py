#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.translations import get_language, translate_locale
from cocktail.events import when
from cocktail.html.element import Element
from cocktail.html import templates
from cocktail.html.utils import rendering_xml
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
            return translate_locale(language, language = language)
        else:
            return translate_locale(language)

    def get_entry_url(self, language):

        publishable = app.publishable

        if (
            self.missing_translations == "redirect"
            and not publishable.is_accessible(language = language)
        ):
            publishable = app.website.home
            translation_url = publishable.get_uri(language = language)
        else:
            translation_url = app.url_mapping.transform_request_url(
                language = language
            )

        return translation_url

    def create_entry_link(self, item):
        link = LinkSelector.create_entry_link(self, item)
        value = self.get_item_value(item)
        link["lang"] = value
        link["hreflang"] = value

        @when(link.ready_stage)
        def set_xml_lang(e):
            if rendering_xml():
                e.source["xml:lang"] = value

        return link

