#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.pkgutils import import_object
from cocktail.schema import \
    Adapter, Collection, String, ErrorList, DictAccessor
from cocktail.controllers import get_parameter, view_state
from sitebasis.models import Site

from sitebasis.controllers.backoffice.basebackofficecontroller \
        import RelationNode

from sitebasis.controllers.backoffice.itemsectioncontroller \
        import ItemSectionController


class ItemFieldsController(ItemSectionController):

    view_class = "sitebasis.views.BackOfficeEditView"
    rich_text_editor_class = "sitebasis.views.RichTextEditor"

    def __init__(self):
        ItemSectionController.__init__(self)
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

    @cached_getter
    def form_data(self):

        form_data = ItemSectionController.form_data(self)                
        section = self.params.read(String("section", default = "fields"))
        rel = self.params.read(String("rel"))
        
        translations = self.translations

        added_translation = self.params.read(
            String("add_translation",
                enumeration = self.available_languages
            )
        )

        deleted_translation = self.params.read(
            String("delete_translation",
                enumeration = translations
            )
        )

        # Load form data from the request
        if self.submitted \
        or section != "fields" \
        or added_translation \
        or deleted_translation \
        or rel:

            from pprint import pprint
            print "<" * 80
            print "Loading form data"

            get_parameter(
                self.form_schema,
                target = form_data,
                languages = translations,
                enable_defaults = False,
                strict = False)

            pprint(cherrypy.request.params)
            pprint(form_data)
            print ">" * 80

            if added_translation and added_translation not in translations:
                translations.append(added_translation)

            if deleted_translation:
                translations.remove(deleted_translation)

        return form_data
    
    def _init_view(self, view):
        
        ItemSectionController._init_view(self, view)

        view.section = "fields"
        view.submitted = self.submitted
        view.edit_stack = self.edit_stack
        view.edited_content_type = self.edited_content_type
        view.edited_item = self.item
        view.form_data = self.form_data
        view.form_schema = self.form_schema
        view.form_errors = self.form_errors
        view.available_languages = self.available_languages
        view.translations = self.translations
        view.differences = self.differences
        view.collections = self.parent.collections

        # Set form displays
        for cls in self.edited_content_type.descend_inheritance(True):
            cls_displays = self.__member_display.get(cls)    
            if cls_displays:
                for key, display in cls_displays.iteritems():
                    view.edit_form.set_member_display(key, display)

    def _save_edit_state(self):
        edit_state = self.edit_node
        edit_state.form_data = self.form_data
        edit_state.translations = self.translations

    def end(self):

        if not self.error or self.redirecting:
            self._save_edit_state()

        rel = self.params.read(String("rel"))

        # Open the item selector
        if rel:     
            # Freeze the reference to the current node
            self.edit_node

            # Push the relation as a new edit node
            member = self.edited_content_type[rel]
            node = RelationNode()
            node.member = member
            self.edit_stack.push(node)
            value = DictAccessor.get(self.form_data, rel)

            raise cherrypy.HTTPRedirect(
                self.cms.uri(self.backoffice, "content")
                + "?" + view_state(
                    selection = value.id if value is not None else None,
                    edit_stack = self.edit_stack.to_param()
                )
            )

        ItemSectionController.end(self)

