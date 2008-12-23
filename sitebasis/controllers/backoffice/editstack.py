#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from copy import copy
import cherrypy
from cocktail.modeling import ListWrapper
from cocktail.schema import Collection, add, remove, DictAccessor
from cocktail.controllers import context


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
        if index < 0:
            index = len(self) + index

        node = self[index]
        
        if isinstance(node, EditNode):
            next_node = self[index + 1] if index + 1 < len(self) else None
            uri = context["cms"].document_uri(
                "content",
                str(node.item.id) if node.item else "new",
                next_node.member.name
                    if next_node and isinstance(next_node, RelationNode)
                        and isinstance(next_node.member, Collection)
                    else "fields"
            )
        else:
            uri = context["cms"].document_uri("content")

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

    @ivar content_type: The type of the edited item.
    @type content_type: L{Item<sitebasis.models.item.Item>} subclass

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

    def collection_has_changes(self, member):
        """Indicates if the given collection has been changed.

        @param member: The collection to evaluate.
        @type member: L{Collection<cocktail.schema.schemacollections.Collection>}

        @return: True if the edit state contains changes for the given
            collection, False if the collection remains unchanged.
        @rtype: bool
        """
        key = member.name
        collection_state = self.__collections.get(key)

        return collection_state is not None \
            and (self.item is None or collection_state != self.item.get(key))

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
            add(collection, item)
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
            remove(collection, item)
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

