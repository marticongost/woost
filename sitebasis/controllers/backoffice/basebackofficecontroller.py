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
from sitebasis.controllers.backoffice.editstack import EditStack, EditNode


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
            params["type"] = target.type

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
        """
        edit_stack = None
        edit_stack_param = self.params.read(
            String("edit_stack", format = r"\d+-\d+"))

        if edit_stack_param:
            id, step = map(int, edit_stack_param.split("-"))
            edit_stack = self.edit_stacks.get(id)
            
            # Prune the stack
            if edit_stack is not None:
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
        return self.edit_stack[-1]

    @getter
    def edit_node(self):
        return first(node
            for node in reversed(list(self.edit_stack))
            if isinstance(node, EditNode))

    @cached_getter
    def output(self):
        output = BaseCMSController.output(self)
        output.update(
            backoffice = self.context["document"],
            section = self.section,
            edit_stack = self.edit_stack
        )
        return output

    @event_handler
    def handle_after_request(cls, event):
        # Preserve the edit session
        event.source.edit_stack
        cherrypy.session["edit_stacks"] = event.source.edit_stacks

