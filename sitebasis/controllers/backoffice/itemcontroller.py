#-*- coding: utf-8 -*-
"""

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
from cocktail.schema import Collection
from cocktail.controllers import view_state, Location

from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController

from sitebasis.controllers.backoffice.editstack import EditNode

from sitebasis.controllers.backoffice.showdetailcontroller \
    import ShowDetailController

from sitebasis.controllers.backoffice.differencescontroller \
    import DifferencesController


class ItemController(BaseBackOfficeController):

    default_section = "fields"
    
    show_detail = ShowDetailController
    differences = DifferencesController

    @cached_getter
    def fields(self):
        return resolve(
            (self.edited_item or self.edited_content_type).edit_controller
        )

    @cached_getter
    def edited_item(self):
        return self.context["cms_item"]

    def resolve(self, path):

        if path:
            collection_name = path.pop(0)

            try:
                member = self.edited_content_type[collection_name]
            except KeyError:
                pass
            else:
                if member in self.collections:
                    return self._get_collection_controller(member)

    def _get_collection_controller(self, member):
        controller_class = resolve(member.edit_controller)
        return controller_class(member)

    @cached_getter
    def edited_content_type(self):
        return (
            self.edited_item and self.edited_item.__class__
            or self.stack_node.content_type
            or self.get_content_type()
        )

    @cached_getter
    def collections(self):
        access_granted = self.context["cms"].authorization.allows
        relation_node = self.relation_node
        stack_relation = relation_node and relation_node.member.related_end

        return [
            member
            for member in self.edited_content_type.ordered_members()
            if isinstance(member, Collection)
            and member.visible
            and member.editable
            and member is not stack_relation
            and access_granted(
                target_instance = self.edited_item,
                target_type = self.edited_content_type,
                action = "read",
                member = member
            )
            and access_granted(
                target_type = member.items.type,
                action = "read",
                partial_match = True
            )
        ]
    
    @cached_getter
    def edit_stack(self):

        edit_stack = self.requested_edit_stack
        redirect = False

        # Spawn a new edit stack
        if edit_stack is None:
            edit_stack = self._new_edit_stack()
            redirect = True

        # Make sure the top node of the stack is an edit node
        if not edit_stack or not isinstance(edit_stack[-1], EditNode):
            edit_state = EditNode()
            edit_state.item = self.edited_item
            edit_state.content_type = (
                self.edited_item and self.edited_item.__class__                
                or self.get_content_type()
            )
            edit_stack.push(edit_state)
            redirect = True
        
        # If the stack is modified a redirection is triggered so that any
        # further request mentions the new stack position in its parameters.
        # However, the redirection won't occur if the controller itself is the
        # final target of the current request - if that is the case, submit()
        # will end up redirecting the user to the default section anyway
        if redirect and self is not cherrypy.request.handler:
            location = Location.get_current()
            location.method = "GET"
            location.params["edit_stack"] = edit_stack.to_param()
            location.go()

        return edit_stack

    @event_handler
    def handle_before_request(cls, event):
        
        controller = event.source

        # Disable access to invisible content types
        if not controller.edited_content_type.visible:
            raise cherrypy.NotFound()

        # Require an edit stack
        controller.edit_stack

        # Restrict access
        controller.context["cms"].authorization.restrict_access(
            target_instance = controller.edited_item,
            action = "read"
        )

    def submit(self):
        self.section_redirection(self.default_section)

    def section_redirection(self, default = None):
        section = cherrypy.request.params.get("section", default)
        if section:
            self.switch_section(section)

    def switch_section(self, section):
        raise cherrypy.HTTPRedirect(
            self.get_edit_uri(
                self.edited_item or self.edited_content_type,
                section
            )
        )

