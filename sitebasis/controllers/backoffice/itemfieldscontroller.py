#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.events import event_handler
from cocktail.pkgutils import import_object
from cocktail.schema import \
    Adapter, Collection, String, ErrorList, DictAccessor
from cocktail.controllers import get_parameter, view_state
from sitebasis.models import Site
from sitebasis.controllers.backoffice.editstack import RelationNode
from sitebasis.controllers.backoffice.editcontroller import EditController


class ItemFieldsController(EditController):

    @cached_getter
    def form_data(self):

        form_data = EditController.form_data(self)                
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
            get_parameter(
                self.form_schema,
                target = form_data,
                languages = translations,
                enable_defaults = False,
                prefix = "edited_item_",
                strict = False)

            if added_translation and added_translation not in translations:
                translations.append(added_translation)

            if deleted_translation:
                translations.remove(deleted_translation)

        return form_data
    
    @cached_getter
    def output(self):
        output = EditController.output(self)
        output.update(
            section = "fields",
            submitted = self.submitted,
            available_languages = self.available_languages
        )
        return output

    @cached_getter
    def view_class(self):
        return self.edited_content_type.edit_view

    def _save_edit_state(self):
        edit_state = self.stack_node
        edit_state.form_data = self.form_data
        edit_state.translations = self.translations

    @event_handler
    def handle_processed(cls, event):

        controller = event.source
        controller._save_edit_state()

        rel = controller.params.read(String("rel"))

        # Open the item selector
        if rel:

            # Push the relation as a new edit node
            member = controller.edited_content_type[rel]
            node = RelationNode()
            node.member = member
            controller.edit_stack.push(node)
            value = DictAccessor.get(controller.form_data, rel)

            raise cherrypy.HTTPRedirect(
                controller.context["cms"].document_uri("content")
                + "?" + view_state(
                    selection = value.id if value is not None else None,
                    edit_stack = controller.edit_stack.to_param()
                )
            )

