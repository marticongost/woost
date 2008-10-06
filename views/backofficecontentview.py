#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
from sitebasis.views.backofficelayout import BackOfficeLayout
from sitebasis.views.contentview import ContentView


class BackOfficeContentView(BackOfficeLayout):

    sections = "content", "history"
    user_collection = None
    available_languages = None
    visible_languages = None
    available_content_views = None
    content_view = None

    def _build(self):
        BackOfficeLayout._build(self)
        self.add_resource("/resources/scripts/jquery.js")
        self.add_resource("/resources/scripts/backoffice_content.js")

    def _ready(self):

        BackOfficeLayout._ready(self)
        
        self.body.append(self.content_view)
        self.content_view["action"] = \
            self.cms.uri(self.backoffice.path, "content")
        self.content_view.cms = self.cms
        self.content_view.backoffice = self.backoffice
        self.content_view.user_collection = self.user_collection
        self.content_view.available_languages = self.available_languages
        self.content_view.visible_languages = self.visible_languages
        self.content_view.available_content_views = \
            self.available_content_views

