#-*- coding: utf-8 -*-
u"""

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
from sitebasis.models import (
    get_current_user,
    Site,
    ModifyPermission,
    CreatePermission
)
from sitebasis.controllers.backoffice.useractions import get_user_action
from sitebasis.controllers.backoffice.editstack import RelationNode
from sitebasis.controllers.backoffice.editcontroller import EditController


class ItemFieldsController(EditController):

    section = "fields"
    form_prefix = "edited_item_"

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
        get_parameter(
            self.fields_schema,
            target = form_data,
            languages = translations,
            enable_defaults = False,
            prefix = self.form_prefix,
            strict = False,
            skip_undefined = cherrypy.request.method.upper() == "GET"
        )

        if added_translation and added_translation not in translations:
            translations.append(added_translation)

        if deleted_translation:
            translations.remove(deleted_translation)
            for key, member in self.fields_schema.members().iteritems():
                if member.translated:
                    values = form_data.get(key)
                    if values:
                        values.pop(deleted_translation, None)
        
        return form_data

    @cached_getter
    def fields_adapter(self):
        adapter = schema.Adapter()
        adapter.exclude([
            member.name
            for member in self.stack_node.content_type.members().itervalues()
            if isinstance(member, schema.Collection) and not member.edit_inline
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
            fields_schema = self.fields_schema,
            selected_action = get_user_action("edit")
        )
        return output

    @cached_getter
    def view_class(self):
        return self.stack_node.item.edit_view

    @event_handler
    def handle_traversed(cls, event):

        # Restrict access to the edited item
        controller = event.source
        item = controller.stack_node.item
        user = get_current_user()
        
        if item.is_inserted:
            user.require_permission(ModifyPermission, target = item)
        else:
            user.require_permission(CreatePermission, target = item.__class__)

    @event_handler
    def handle_processed(cls, event):

        controller = event.source
        rel = controller.params.read(schema.String("rel"))

        # Open the item selector
        if rel:

            pos = rel.find("-")
            root_content_type_name = rel[:pos]
            selection_parameter = rel[pos + 1:]
            key = selection_parameter[len(controller.form_prefix):]

            # Push the relation as a new stack node
            current_node = controller.stack_node
            rel_node = RelationNode()
            rel_node.member = current_node.content_type[key]
            controller.edit_stack.push(rel_node)

            value = schema.get(current_node.form_data, key)

            raise cherrypy.HTTPRedirect(
                controller.context["cms"].document_uri("content")
                + "?" + view_state(
                    selection = value.id if value is not None else None,
                    edit_stack = controller.edit_stack.to_param()
                )
            )

