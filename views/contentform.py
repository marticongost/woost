#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.translations import translate
from cocktail.schema import Collection, Reference
from cocktail.html import Element, templates

Form = templates.get_class("cocktail.html.Form")


class ContentForm(Form):

    def _build(self):

        Form._build(self)

        self.set_member_type_display(Reference, "sitebasis.views.ItemSelector")

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

    def create_fieldset(self, group):

        if group.id == "translations":
            fieldset = Element("table")
            fieldset.add_class(group.id)
        else:
            fieldset = Form.create_fieldset(self, group)

        return fieldset

    def create_field(self, member):
        
        field_entry = Form.create_field(self, member)

        if member.translated and not self.get_member_hidden(member):
            field_entry.tag = "tr"

        return field_entry

    def create_label_container(self, member):
        container = Form.create_label_container(self, member)

        if member.translated:
            container.tag = "td"
            container.add_class("lable_container")

        return container
    
    def create_control_container(self, member):
        container = Form.create_control_container(self, member)

        if member.translated:
            container.tag = "td"
            container.add_class("control_container")

        return container

    def create_translation_headers(self):

        headers = Element("tr")
        headers.add_class("translation_headers")
        headers.append(Element("td"))
    
        for language in self.translations:
            header = self.create_language_header(language)
            headers.append(header)

        return headers

    def create_language_header(self, language):
        
        header = Element("td")
        header.add_class("language")
        
        label = Element("span")
        label.append(translate(language))
        header.append(label)

        return header

