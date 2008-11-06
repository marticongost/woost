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
import cherrypy
from cocktail.modeling import cached_getter, ListWrapper
from cocktail.language import get_content_language
from cocktail.controllers import \
    get_parameter, get_persistent_param, BaseController
from sitebasis.models import Item
from sitebasis.controllers import Request
from cocktail.schema import String, Integer


class BaseBackOfficeController(BaseController):

    section = None
    persistent_content_type_choice = False
    settings_duration = 60 * 60 * 24 * 30 # ~= 1 month

    def __init__(self):
        BaseController.__init__(self)
        self.__edit_stacks_lock = Lock()

    @cached_getter
    def backoffice(self):
        return Request.current.document

    @cached_getter
    def cms(self):
        return Request.current.cms

    @cached_getter
    def user(self):
        return self.cms.authentication.user

    def _init_view(self, view):
        BaseController._init_view(self, view)
        view.backoffice = self.backoffice
        view.cms = self.cms
        view.user = self.user
        view.section = self.section
        view.edit_stack = self.edit_stack

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
            for entity in chain([Item], Item.derived_entities()):
                if entity.__name__ == type_param:
                    return entity

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
        parameter (see the L{requested_edit_stack} property), but some
        subclasses override this property in order to create a new stack if
        none is selected.
        
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

    @cached_getter
    def edit_node(self):
        return self.edit_stack[-1]

    def end(self):
        # Preserve the edit session
        self.edit_stack
        cherrypy.session["edit_stacks"] = self.edit_stacks
        

class EditStack(ListWrapper):
    """A stack describing the context of an edit session. Allows to keep track
    of nested edit operations when dealing with related elements.

    The stack can contain two kind of nodes:

        * L{EditState} nodes are associated with a single
          L{item<sitebasis.models.items.Item>}, and store all the changes
          performed on it before they are finally saved.

        * Relation nodes can take the form of a
          L{collection<cocktail.schema.schemacollections.Collection>} or a
          L{relation<cocktail.schema.schemarelations.Relation>} member, and
          indicate a nested edit operation on a related item or set of items.

    The first node of a stack is always an L{EditState} node. All further nodes
    alternate their kind in succession (so the first L{EditState} node will be
    followed by a relation node, then another L{EditState} node, and so on).

    @ivar id: A numerical identifier for the stack. It is guaranteed to be
        unique throughout the current browser session.
    """
    id = None

    def push(self, node):
        """Adds a new node to the edit stack.

        @param node: The node to add.
        @type node: L{EditState},
            L{collection<cocktail.schema.schemacollections.Collection>}
            or L{relation<cocktail.schema.schemarelations.Relation>}
        """
        self._items.append(node)

    def pop(self):
        """Removes the last node from the stack and returns it.

        @return: The last node of the stack.
        @rtype: L{EditState},
            L{collection<cocktail.schema.schemacollections.Collection>}
            or L{relation<cocktail.schema.schemarelations.Relation>}

        @raise IndexError: Raised when trying to pop a node from an empty
            stack.
        """
        return self._items.pop()

    def go(self, offset):

        node = self[len(self) - 1 + offset]
        
        if isinstance(node, EditState):
            uri = Request.current.uri(
                "content",
                str(node.item.id) if node.item else "new"
            )
        else:
            uri = Request.current.uri("content")

        uri += "?edit_stack=" + self.to_param(offset)
        raise cherrypy.HTTPRedirect(uri)

    def to_param(self, offset = 0):
        return "%d-%d" % (self.id, len(self) -1 + offset)


class EditState(object):

    def __init__(self):
        self.id = None
        self.item = None
        self.content_type = None
        self.form_data = None
        self.translations = None

