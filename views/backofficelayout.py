#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from cocktail.translations import translate
from cocktail.html import Element


class BackOfficeLayout(Element):

    cms = None
    backoffice = None
    user = None
    sections = None
    section = None

    def _build(self):
 
        self.add_resource("/resources/styles/backoffice.css")

        self.header = self.create_header()
        self.append(self.header)
        
        self.navigation = self.create_navigation()
        self.append(self.navigation)

        self.body = self.create_body()        
        self.append(self.body)

        self.footer = self.create_footer()
        self.append(self.footer)

    def _ready(self):
        
        if self.backoffice:
            if self.page_title is None:
                self.page_title = translate(self.backoffice)

            for resource in self.backoffice.resources:
                self.add_resource(resource.uri)

        self._fill_title()
        self._fill_identity_info()
        self._fill_sections()

        Element._ready(self)

    def _fill_title(self):
        self.title.value = self.page_title or ""

    def _fill_identity_info(self):
        if self.user and not self.user.anonymous:
            self.identity_info.label.value = translate(
                "logged in as",
                user = self.user)
        else:
            self.identity_info.visible = False

    def _fill_sections(self):
        if self.sections:
            for section in self.sections:
                section_entry = self.create_section_entry(section)
                self.navigation.append(section_entry)                

    def create_header(self):
        
        header = Element()
        header.add_class("header")
        
        self.title = Element("h1")
        header.append(self.title)

        self.identity_info = self.create_identity_info()
        header.append(self.identity_info)

        return header    

    def create_identity_info(self):
        
        identity = Element()
        identity.add_class("identity")

        identity.label = Element("span")
        identity.append(identity.label)

        identity.form = Element("form", method = "post")
        identity.append(identity.form)

        identity.logout_button = Element("button",
            name = "logout",
            type = "submit")
        identity.logout_button.append(translate("Logout"))
        identity.form.append(identity.logout_button)

        return identity

    def create_navigation(self):        
        navigation = Element()
        navigation.add_class("navigation")
        return navigation

    def create_body(self):
        body = Element()
        body.add_class("body")
        return body

    def create_footer(self):
        footer = Element()
        footer.add_class("footer")
        return footer

    def create_section_entry(self, section):

        section_id = self.get_section_id(section)

        entry = Element("a")
        entry.add_class("section")
        entry.add_class(section_id + "_section")
        entry["href"] = self.get_section_url(section)
        entry.append(self.get_section_label(section))

        setattr(self, section_id + "_section", entry)

        if section_id == self.section:
            entry.add_class("selected")
        
        return entry

    def get_section_id(self, section):
        return section

    def get_section_label(self, section):
        return translate(section + "_section")

    def get_section_url(self, section):
        return self.cms.uri(self.backoffice.path, section)
    
