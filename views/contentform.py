#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.translations import translate
from cocktail.schema import Collection
from cocktail.html import Element, templates

Form = templates.get_class("cocktail.html.Form")


class ContentForm(Form):

    def _build(self):

        Form._build(self)

        self.add_group(
            "properties",
            lambda member: not isinstance(member, Collection) \
                           and not member.translated
        )

        self.add_group(
            "translations",
            lambda member: not isinstance(member, Collection) \
                           and member.translated
        )

    def _ready(self):

        Form._ready(self)

        if self.translations:
            headers = self.create_translation_headers()
            self.translations_fieldset.insert(0, headers)

    def create_translation_headers(self):

        headers = Element("div")
        headers.add_class("translation_headers")
    
        for language in self.translations:
            header = self.create_language_header(language)
            headers.append(header)

        return headers

    def create_language_header(self, language):
        
        header = Element("div")
        header.add_class("language")
        
        label = Element("span")
        label.append(translate(language))
        header.append(label)

        return header

