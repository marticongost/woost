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
from cocktail import schema
from cocktail.controllers import get_parameter, view_state
from sitebasis.models import Site
from sitebasis.controllers.backoffice.editstack import RelationNode
from sitebasis.controllers.backoffice.editcontroller import EditController


class ItemFieldsController(EditController):

    section = "fields"

    def __call__(self, *args, **kwargs):
        self._handle_form_data()
        return EditController.__call__(self, *args, **kwargs)

    def _handle_form_data(self):

        stack_node = self.stack_node
        form_data = stack_node.form_data
        translations = stack_node.translations

        section = self.params.read(
            schema.String("section", default = "fields")
        )
        rel = self.params.read(schema.String("rel"))

        added_translation = self.params.read(
            schema.String("add_translation",
                enumeration = self.available_languages
            )
        )

        deleted_translation = self.params.read(
            schema.String("delete_translation",
                enumeration = translations
            )
        )

        # Load form data from the request
        if self.submitted \
        or section != self.section \
        or added_translation \
        or deleted_translation \
        or rel:
            get_parameter(
                self.fields_schema,
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
    def fields_adapter(self):
        adapter = schema.Adapter()
        adapter.exclude([
            member.name
            for member in self.stack_node.content_type.members().itervalues()
            if isinstance(member, schema.Collection)
        ])
        return adapter

    @cached_getter
    def fields_schema(self):
        fields_schema = self.fields_adapter.export_schema(
            self.stack_node.form_schema
        )
        fields_schema.name = "BackOfficeEditForm"
        return fields_schema

    @cached_getter
    def output(self):
        output = EditController.output(self)
        output.update(
            submitted = self.submitted,
            available_languages = self.available_languages,
            fields_schema = self.fields_schema
        )
        return output

    @cached_getter
    def view_class(self):
        return self.stack_node.item.edit_view

    @event_handler
    def handle_processed(cls, event):

        controller = event.source
        rel = controller.params.read(schema.String("rel"))

        # Open the item selector
        if rel:

            # Push the relation as a new stack node
            current_node = controller.stack_node
            rel_node = RelationNode()
            rel_node.member = current_node.content_type[rel]
            controller.edit_stack.push(rel_node)

            value = schema.get(current_node.form_data, rel)

            raise cherrypy.HTTPRedirect(
                controller.context["cms"].document_uri("content")
                + "?" + view_state(
                    selection = value.id if value is not None else None,
                    edit_stack = controller.edit_stack.to_param()
                )
            )

