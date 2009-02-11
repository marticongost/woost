#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement
from itertools import chain
from threading import Lock
from urllib import urlencode
import cherrypy
from cocktail.modeling import getter, cached_getter
from cocktail.iteration import first
from cocktail.events import event_handler
from cocktail.schema import String
from cocktail.language import get_content_language
from cocktail.controllers import get_persistent_param
from sitebasis.models import Item
from sitebasis.controllers import BaseCMSController
from sitebasis.controllers.backoffice.useractions import get_user_action
from sitebasis.controllers.backoffice.editstack import (
    EditStack, EditNode, RelationNode
)


class BaseBackOfficeController(BaseCMSController):

    section = None
    persistent_content_type_choice = False
    settings_duration = 60 * 60 * 24 * 30 # ~= 1 month

    def __init__(self, *args, **kwargs):
        BaseCMSController.__init__(self, *args, **kwargs)
        self.__edit_stacks_lock = Lock()

    def get_edit_uri(self, target, *args, **kwargs):
        
        params = kwargs or {}
        edit_stack = self.edit_stack

        if edit_stack:
            params["edit_stack"] = edit_stack.to_param()

        # URI for new items
        if isinstance(target, type):
            target_id = "new"
            
            # TODO: Use full names to identify types
            if not edit_stack:
                params["type"] = target.name

        # URI for existing items
        else:
            primary_member = target.__class__.primary_member
            
            if primary_member is None:
                raise TypeError("Can't edit types without a primary member")

            target_id = target.get(primary_member)

            if target_id is None:
                raise ValueError("Can't edit objects without an identifier")
        
        uri = self.document_uri(
            "content",
            target_id,
            *args
        )

        if params:
            uri += "?" + urlencode(params, True)

        return uri

    def get_content_type(self, default = None):

        if self.persistent_content_type_choice:
            type_param = get_persistent_param(
                "type",
                cookie_duration = self.settings_duration
            )
        else:
            type_param = cherrypy.request.params.get("type")

        if type_param is None:
            return default
        else:
            for content_type in chain([Item], Item.derived_schemas()):
                if content_type.__name__ == type_param:
                    return content_type

    def get_visible_languages(self):

        param = get_persistent_param(
            "language",
            cookie_name = "visible_languages",
            cookie_duration = self.settings_duration
        )

        if param is not None:
            if isinstance(param, (list, tuple, set)):
                return set(param)
            else:
                return set(param.split(","))
        else:
            return [get_content_language()]

    @cached_getter
    def edit_stacks(self):
        """A mapping containing all the edit stacks for the current HTTP
        session.

        @return: The mapping of stacks, indexed by their numerical id.
        @rtype: mapping of int => L{EditStack}
        """
        edit_stacks = cherrypy.session.get("edit_stacks")
        
        if edit_stacks is None:

            with self.__edit_stacks_lock:
                edit_stacks = cherrypy.session.get("edit_stacks")

                if edit_stacks is None:
                    edit_stacks = {}
                    cherrypy.session["edit_stacks"] = edit_stacks

        return edit_stacks

    @cached_getter
    def edit_stack(self):
        """Obtains the stack of edit operations that applies to the current
        context. The active stack is usually selected through an HTTP
        parameter.
        
        @return: The current edit stack.
        @rtype: L{EditStack}
        """
        return self.requested_edit_stack

    @cached_getter
    def requested_edit_stack(self):
        """
        Obtains the stack of edit operations for the current HTTP request, as
        indicated by an HTTP parameter ("edit_stack").

        @return: The current edit stack, or None if the "edit_stack" parameter
            is missing or the indicated id doesn't match an active stack.
        @rtype: L{EditStack}

        @raise EditStateLostError: Raised if the user requests an edit stack
            that is no longer available.
        """
        edit_stack = None
        edit_stack_param = self.params.read(
            String("edit_stack", format = r"\d+-\d+"))

        if edit_stack_param:
            id, step = map(int, edit_stack_param.split("-"))
            edit_stack = self.edit_stacks.get(id)
    
            # Edit state lost
            if edit_stack is None:
                raise EditStateLostError()

            # Prune the stack
            else:
                while len(edit_stack) > step + 1:
                    edit_stack.pop()                    
        
        return edit_stack

    def _new_edit_stack(self):
        
        edit_stack = EditStack()

        with self.__edit_stacks_lock:
            edit_stack.id = cherrypy.session.get("edit_stacks_id", 0)
            cherrypy.session["edit_stacks_id"] = edit_stack.id + 1

        self.edit_stacks[edit_stack.id] = edit_stack
        return edit_stack

    @getter
    def stack_node(self):
        stack = self.edit_stack
        return stack and stack[-1]

    @getter
    def edit_node(self):
        stack = self.edit_stack
        return stack and first(node
            for node in reversed(list(stack))
            if isinstance(node, EditNode))

    @getter
    def relation_node(self):
        stack = self.edit_stack
        return stack and first(node
            for node in reversed(list(stack))
            if isinstance(node, RelationNode))

    @cached_getter
    def output(self):
        output = BaseCMSController.output(self)
        output.update(
            backoffice = self.context["document"],
            section = self.section,
            edit_stack = self.edit_stack
        )
        return output

    def _invoke_user_action(self, action, selection):
        for error in action.get_errors(self, selection):
            raise error

        action.invoke(self, selection)

    def _get_user_action(self, param_key = "action"):
        action = None
        action_id = self.params.read(String(param_key))
        
        if action_id:
            action = get_user_action(action_id)
            if action and not action.enabled:
                action = None

        return action

    def go_back(self):
        """Redirects the user to its previous significant location."""

        edit_stack = self.edit_stack

        # Go back to the parent edit state
        if edit_stack and len(edit_stack) > 1:
            if isinstance(edit_stack[-2], RelationNode):
                edit_stack.go(-3)
            else:
                edit_stack.go(-2)
        
        # Go back to the root of the backoffice
        else:
            raise cherrypy.HTTPRedirect(self.document_uri())


class EditStateLostError(Exception):
    """An exception raised when a user requests an edit state that is no longer
    available."""

