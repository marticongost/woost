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
from cocktail.controllers import context
from woost.models import Language

LinkSelector = templates.get_class("cocktail.html.LinkSelector")


class LanguageSelector(LinkSelector):

    translated_labels = True
    tag = "ul"

    def create_entry(self, value, label, selected):        
        
        entry = Element("li")
        link = self.create_entry_link(value, label)

        if selected:
            strong = Element("strong")
            strong.append(link)
            entry.append(strong)
        else:
            entry.append(link)

        return entry

    def _ready(self):
        
        if self.items is None:
            self.items = Language.codes

        if self.value is None:
            self.value = get_language()

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
        return cms.translate_uri(language = language)

