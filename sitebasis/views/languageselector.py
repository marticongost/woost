#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.language import get_content_language
from cocktail.translations import translate
from cocktail.html import templates
from cocktail.controllers import context
from sitebasis.models import Language

LinkSelector = templates.get_class("cocktail.html.LinkSelector")


class LanguageSelector(LinkSelector):

    translated_labels = True

    def _ready(self):
        
        if self.items is None:
            self.items = Language.codes

        if self.value is None:
            self.value = get_content_language()

        LinkSelector._ready(self)

    def get_item_label(self, language):
        if self.translated_labels:
            return translate(language, language)
        else:
            return translate(language)

    def get_entry_url(self, language):
        return context["cms"].language.translate_uri(language)

