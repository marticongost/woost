#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from threading import Lock
import cherrypy
from cocktail.modeling import cached_getter, getter
from cocktail.events import event_handler
from cocktail.pkgutils import resolve
from cocktail import schema
from cocktail.controllers import (
    view_state,
    get_parameter,
    get_request_url_builder
)
from woost import app
from woost.models import (
    Item,
    ReadPermission
)

from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController

from woost.controllers.backoffice.editstack import EditNode, RelationNode

from woost.controllers.backoffice.installationsynccontroller \
    import InstallationSyncController

from woost.controllers.backoffice.referencescontroller \
    import ReferencesController


class ItemController(BaseBackOfficeController):

    default_section = "fields"

    installation_sync = InstallationSyncController
    references = ReferencesController

    @cached_getter
    def preview(self):
        return resolve(self.stack_node.item.preview_controller)

    @cached_getter
    def fields(self):
        return resolve(self.stack_node.item.edit_controller)

    @event_handler
    def handle_traversed(cls, event):

        controller = event.source

        # Require an edit stack with an edit node on top
        controller._require_edit_node()

        # Disable access to invisible content types
        if not controller.stack_node.content_type.visible:
            raise cherrypy.NotFound()

        # Restrict access
        if controller.stack_node.item.is_inserted:
            app.user.require_permission(
                ReadPermission,
                target = controller.stack_node.item
            )

    def _require_edit_node(self):

        redirect = False
        context_item = self.context["cms_item"]
        edit_stacks_manager = self.context["edit_stacks_manager"]
        edit_stack = edit_stacks_manager.current_edit_stack

        # Spawn a new edit stack
        if edit_stack is None:
            edit_stack = edit_stacks_manager.create_edit_stack()
            edit_stacks_manager.current_edit_stack = edit_stack
            redirect = True
        else:
            # Integral part; add a new relation node (won't be shown to the
            # user)
            member_name = self.params.read(schema.String("member"))

            if member_name:
                node = RelationNode()
                node.member = edit_stack[-1].content_type[member_name]

                # Preserve the selected tab
                group = node.member.member_group
                if group:
                    pos = group.find(".")
                    if pos != -1:
                        group = group[:pos]
                edit_stack[-1].tab = group

                edit_stack.push(node)
                redirect = True

        # Make sure the top node of the stack is an edit node
        if not edit_stack \
        or not isinstance(edit_stack[-1], EditNode) \
        or (context_item and context_item.id != edit_stack[-1].item.id):

            # New item
            if context_item is None:
                content_type = get_parameter(
                    schema.Reference("item_type", class_family = Item)
                )
                item = content_type()
            # Existing item
            else:
                item = context_item

            e = self.context["cms"].choosing_visible_translations(
                item = item,
                visible_translations = set(
                    app.user.backoffice_visible_translations
                    or self.visible_languages
                )
            )

            node_class = resolve(item.edit_node_class)
            node = node_class(
                item,
                visible_translations = e.visible_translations
            )
            edit_stack.push(node)
            redirect = True

        # If the stack is modified a redirection is triggered so that any
        # further request mentions the new stack position in its parameters.
        # However, the redirection won't occur if the controller itself is the
        # final target of the current request - if that is the case, submit()
        # will end up redirecting the user to the default section anyway
        if redirect and self is not cherrypy.request.handler:
            url_builder = get_request_url_builder()
            url_builder.query["edit_stack"] = edit_stack.to_param()
            url_builder.query.pop("member", None)
            url_builder.fragment = ""
            raise cherrypy.HTTPRedirect(url_builder.get_url())

        return edit_stack

    def submit(self):
        self.section_redirection(self.default_section)

    def section_redirection(self, default = None):
        section = cherrypy.request.params.get("section", default)
        if section:
            self.switch_section(section)

    def switch_section(self, section):
        item = self.stack_node.item

        # Preserve form initialization parameters
        if cherrypy.request.method == "GET":
            params = dict(
                (key, value)
                for key, value in cherrypy.request.params.iteritems()
                if key.startswith("edited_item_")
            )
        else:
            params = {}

        raise cherrypy.HTTPRedirect(
            self.edit_uri(
                item if item.is_inserted else item.__class__,
                section,
                **params
            )
        )

