#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement
from copy import copy
from itertools import chain
from threading import Lock
import cherrypy
from cocktail.modeling import cached_getter, ListWrapper
from cocktail.schema import DictAccessor, Collection
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

        * L{edit nodes<EditNode>} are associated with a single
          L{item<sitebasis.models.items.Item>}, and store all the changes
          performed on it before they are finally saved.

        * L{relation nodes<RelationNode>} indicate a nested edit operation on a
          related item or set of items.

    The first node of a stack is always an edit node. All further nodes
    alternate their kind in succession (so the first node will be followed by a
    relation node, then another edit node, and so on).

    @ivar id: A numerical identifier for the stack. It is guaranteed to be
        unique throughout the current browser session.
    """
    id = None

    def push(self, node):
        """Adds a new node to the edit stack.

        @param node: The node to add.
        @type node: L{EditNode},
            L{collection<cocktail.schema.schemacollections.Collection>}
            or L{relation<cocktail.schema.schemarelations.Relation>}
        """
        self._items.append(node)

    def pop(self):
        """Removes the last node from the stack and returns it.

        @return: The last node of the stack.
        @rtype: L{EditNode},
            L{collection<cocktail.schema.schemacollections.Collection>}
            or L{relation<cocktail.schema.schemarelations.Relation>}

        @raise IndexError: Raised when trying to pop a node from an empty
            stack.
        """
        return self._items.pop()

    def go(self, index = -1):
        """Redirects the user to the indicated node of the edit stack.

        @param index: The position of the stack to move to.
        @type index: int
        """
        node = self[index]
        
        if isinstance(node, EditNode):
            uri = Request.current.uri(
                "content",
                str(node.item.id) if node.item else "new"
            )
        else:
            uri = Request.current.uri("content")

        uri += "?edit_stack=" + self.to_param(index)
        raise cherrypy.HTTPRedirect(uri)

    def to_param(self, index = -1):
        if index < 0:
            index = len(self) + index

        return "%d-%d" % (self.id, index)


class EditNode(object):
    """An L{edit stack<EditStack>} node, used to maintain a set of changes for
    an edited item before they are finally committed.

    @ivar item: A reference to the item being edited. It will be None when
        creating a new item.
    @type item: L{Item<sitebasis.models.item.Item>}

    @ivar content_type: The entity type of the edited item.
    @type content_type: L{Entity<cocktail.persistence.entity.Entity>} subclass

    @ivar form_data: The complete modified state of the edited item.
    
    @ivar translations: The list of translations defined by the item (note that
        these can change during the course of an edit operation, so that's why
        they are stored in here).
    @type translations: str list 
    """

    def __init__(self):
        self.item = None
        self.content_type = None
        self.form_data = None
        self.translations = None
        self.__collections = {}

    def get_collection(self, member, require_copy = False):
        """Obtains the requested collection from the edited item.

        @param member: The member matching the collection to retrieve.
        @type member: L{Collection<cocktail.schema.schemacollections.Collection>}

        @param require_copy: When set to True, the method will produce a copy
            of the item's collection, and store it for further requests. This
            should be set to True by any call that plans to alter the requested
            collection.
        @type require_copy: bool

        @return: The requested collection.
        """

        key = member.name
        collection = self.__collections.get(key)

        if collection is None:
            if self.item:
                collection = self.item.get(key)

                if require_copy:
                    collection = copy(collection)
                    self.__collections[key] = collection
            else:
                collection = member.produce_default()
                self.__collections[key] = collection

        return collection

    def relate(self, member, item):
        """Adds a relation between the edited item and another item.
        
        @param member: The member describing the relation between the two
            items. It should be the end nearer to the edited item.
        @type member: L{Collection<cocktail.schema.schemacollections.Collection>}
            or L{Reference<cocktail.schema.schemareference.Reference>}

        @param item: The item to relate.
        @type item: L{Item<sitebasis.models.item.Item>}
        """
        if isinstance(member, Collection):
            collection = self.get_collection(member, True)
            collection.add(item)
        else:
            DictAccessor.set(self.form_data, member.name, item)

    def unrelate(self, member, item):
        """Breaks the relation between the edited item and one of its related
        items.
        
        @param member: The member describing the relation between the two
            items. It should be the end nearer to the edited item.
        @type member: L{Collection<cocktail.schema.schemacollections.Collection>}
            or L{Reference<cocktail.schema.schemareference.Reference>}

        @param item: The item to unrelate.
        @type item: L{Item<sitebasis.models.item.Item>}
        """
        if isinstance(member, Collection):
            collection = self.get_collection(member, True)
            collection.remove(item)
        else:
            DictAccessor.set(self.form_data, member.name, None)


class RelationNode(object):
    """An L{edit stack<EditStack>} node, used to maintain data about an action
    affecting a relation.
    
    @var member: The member describing the relation that is being modified.
    @type member: L{Collection<cocktail.schema.schemacollections.Collection>}
        or L{Reference<cocktail.schema.schemareference.Reference>}

    @var action: Can be one of 'add' or 'remove'.
    @type action: str
    """
    member = None
    action = None

