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
from cocktail.schema import Collection, String
from cocktail.controllers import view_state, Location

from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController

from sitebasis.controllers.backoffice.editstack import EditNode, RelationNode

from sitebasis.controllers.backoffice.showdetailcontroller \
    import ShowDetailController

from sitebasis.controllers.backoffice.differencescontroller \
    import DifferencesController


class ItemController(BaseBackOfficeController):

    default_section = "fields"
    
    show_detail = ShowDetailController
    diff = DifferencesController

    @cached_getter
    def fields(self):
        return resolve(self.stack_node.item.edit_controller)

    def resolve(self, path):

        if path:
            collection_name = path.pop(0)

            try:
                member = self.stack_node.content_type[collection_name]
            except KeyError:
                pass
            else:
                if member in self.collections:
                    return self._get_collection_controller(member)

    def _get_collection_controller(self, member):
        controller_class = resolve(member.edit_controller)
        return controller_class(member)

    @cached_getter
    def collections(self):
        
        relation_node = self.relation_node
        stack_relation = relation_node and relation_node.member.related_end

        return [
            member
            for member in self.stack_node.content_type.ordered_members()
            if isinstance(member, Collection)
            and member.visible
            and member.editable
            and member is not stack_relation
            and self.allows(
                target_instance = self.stack_node.item,
                action = "read",
                member = member
            )
            and self.allows(
                target_type = member.items.type,
                action = "read",
                partial_match = True
            )
        ]
    
    @event_handler
    def handle_traversed(cls, event):
        
        controller = event.source

        # Require an edit stack with an edit node on top
        controller._require_edit_node()

        # Disable access to invisible content types
        if not controller.stack_node.content_type.visible:
            raise cherrypy.NotFound()

        # Restrict access
        controller.restrict_access(
            target_instance = controller.stack_node.item,
            action = "read"
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
            member_name = self.params.read(String("member"))

            if member_name:
                node = RelationNode()
                node.member = edit_stack[-1].content_type[member_name]
                edit_stack.push(node)
                redirect = True

        # Make sure the top node of the stack is an edit node
        if not edit_stack \
        or not isinstance(edit_stack[-1], EditNode) \
        or (context_item and context_item.id != edit_stack[-1].item.id):
            
            # New item
            if context_item is None:
                content_type = self.get_content_type()
                item = content_type()

                # Start with a translation object for each visible language
                if content_type.translated:
                    for language in self.get_visible_languages():
                        item._new_translation(language)

            # Existing item
            else:
                item = context_item
            
            node_class = resolve(item.edit_node_class)
            node = node_class(item)
            edit_stack.push(node)
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
            location.params.pop("member", None)
            location.go()

        return edit_stack

    def submit(self):
        self.section_redirection(self.default_section)

    def section_redirection(self, default = None):
        section = cherrypy.request.params.get("section", default)
        if section:
            self.switch_section(section)

    def switch_section(self, section):
        item = self.stack_node.item
        raise cherrypy.HTTPRedirect(
            self.get_edit_uri(
                item if item.is_inserted else item.__class__,
                section
            )
        )

