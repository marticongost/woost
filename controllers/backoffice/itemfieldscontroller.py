#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.pkgutils import import_object
from cocktail.schema import Adapter, Collection, String, ErrorList
from sitebasis.models import Site
from sitebasis.controllers.backoffice.basebackofficecontroller \
        import BaseBackOfficeController


class ItemFieldsController(BaseBackOfficeController):

    view_class = "sitebasis.views.BackOfficeEditView"
    rich_text_editor_class = "sitebasis.views.RichTextEditor"

    def __init__(self):
        BaseBackOfficeController.__init__(self)
        self.__member_display = {}
        self._setup_member_displays()

    def set_member_display(self, member_ref, display):

        pos = member_ref.rfind(".")
        cls_name = member_ref[:pos]
        member_name = member_ref[pos + 1:]

        cls = import_object(cls_name)
        cls_displays = self.__member_display.get(cls)

        if cls_displays is None:
            cls_displays = {}
            self.__member_display[cls] = cls_displays

        cls_displays[member_name] = display

    def _setup_member_displays(self):

        self.set_member_display(
            "sitebasis.models.Document.description",
            self.rich_text_editor_class
        )

        self.set_member_display(
            "sitebasis.models.StandardPage.body",
            self.rich_text_editor_class
        )

    def end(self):
        BaseBackOfficeController.end(self)
        self.parent.save_edit_state()

    def _init_view(self, view):
        
        BaseBackOfficeController._init_view(self, view)

        view.section = "fields"
        view.submitted = self.parent.submitted
        view.edit_state = self.parent.edit_state
        view.content_type = self.parent.content_type
        view.edited_item = self.parent.item
        view.form_data = self.parent.form_data
        view.form_schema = self.parent.form_schema
        view.form_errors = self.parent.form_errors
        view.available_languages = self.parent.available_languages
        view.translations = self.parent.translations
        view.differences = self.parent.differences
        view.collections = self.parent.collections

        # Set form displays
        for cls in self.parent.content_type.descend_inheritance(True):
            cls_displays = self.__member_display.get(cls)    
            if cls_displays:
                for key, display in cls_displays.iteritems():
                    view.edit_form.set_member_display(key, display)

