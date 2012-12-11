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
from woost.models import Language, Site

LinkSelector = templates.get_class("cocktail.html.LinkSelector")


class LanguageSelector(LinkSelector):

    tag = "ul"
    translated_labels = True
    missing_translations = "redirect" # "redirect", "hide", "disable"
    autohide = True

    def create_entry(self, value, label, selected):

        entry = Element("li")
        link = self.create_entry_link(value, label)

        if selected:
            strong = Element("strong")
            strong.append(link)
            entry.append(strong)
        else:
            entry.append(link)

        if self.missing_translations != "redirect":
            publishable = context["publishable"]
            if not publishable.is_accessible(language = value):
                if self.missing_translations == "hide":
                    entry.visible = False
                elif self.missing_translations == "disable":
                    link.tag = "span"
                    link["href"] = None

        return entry

    def _ready(self):

        if self.items is None:
            self.items = [
                language.iso_code 
                for language in Language.select() 
                if language.enabled
            ]

        if self.value is None:
            self.value = get_language()

        if not self.autohide or len(self.items) > 1:
            LinkSelector._ready(self)

            # Hack for IE <= 6
            if self.children:
                self.children[-1].add_class("last")

    def get_item_label(self, language):
        if self.translated_labels:
            return translations(language, language)
        else:
            return translations(language)

    def get_entry_url(self, language):
        cms = context["cms"]
        publishable = context["publishable"]

        if self.missing_translations == "redirect" \
        and not publishable.is_accessible(language = language):
            path = "/"
        else:
            path = None

        return cms.translate_uri(path = path, language = language)

    def create_entry_link(self, value, label):
        link = LinkSelector.create_entry_link(self, value, label)
        link["lang"] = value
        link["hreflang"] = value

        @link.when_ready
        def set_xml_lang():
            if rendering_xml():
                link["xml:lang"] = value

        return link

