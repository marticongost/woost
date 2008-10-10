#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.translations import translate
from cocktail.schema import Collection, DictAccessor
from cocktail.html import Element
from sitebasis.models import Site
from sitebasis.views import templates

BackOfficeLayout = templates.get_class("sitebasis.views.BackOfficeLayout")
ContentForm = templates.get_class("sitebasis.views.ContentForm")


class BackOfficeEditView(BackOfficeLayout):
    
    sections = ["fields"]

    edited_item = None
    content_type = None
    form_schema = None
    form_data = None
    saved = None 

    def _build(self):
        BackOfficeLayout._build(self)        
        self.edit_form = self.create_edit_form()
        self.body.append(self.edit_form)

    def _ready(self):

        if self.edited_item:
            self.page_title = translate(self.edited_item)
        else:
            self.page_title = translate("new " + self.content_type.name)

        # Confine each item collection to its own tab
        self.sections = list(self.sections)
        self.sections.extend(
            member
            for member in self.form_schema.members().itervalues()
            if isinstance(member, Collection) \
            and not member.name in ("changes", "drafts", "translations")
        )

        BackOfficeLayout._ready(self)
        
        # 'Go back' link
        self.navigation.append(
            Element(
                "a", "go_back",
                href = self.cms.uri(self.backoffice.path),
                children = [translate("Go back")]
            )
        )

        self.edit_form.insert(0, self.navigation)

        self.edit_form.data = self.form_data
        self.edit_form.schema = self.form_schema
        
        if self.content_type.translated:
            if self.edited_item:
                self.edit_form.translations = \
                    self.edited_item.translations.keys()
            else:
                self.edit_form.translations = Site.main.languages

    def get_page_title(self):
        if self.edited_item:
            return translate("editing", item = self.edited_item)
        else:
            return translate("creating", content_type = self.content_type)

    def get_section_id(self, section):
        if isinstance(section, Collection):
            return section.name
        else:
            return section

    def get_section_label(self, section):
        if isinstance(section, Collection):
            return translate(section)
        else:
            return BackOfficeLayout.get_section_label(self, section)

    def get_section_url(self, section):
        if isinstance(section, Collection):
            return self.cms.uri(self.backoffice.path, section.name)
        else:
            return BackOfficeLayout.get_section_url(self, section)        

    def create_edit_form(self):

        form = ContentForm()
        form.add_class("edit_form")
        form.accessor = DictAccessor      
    
        return form

