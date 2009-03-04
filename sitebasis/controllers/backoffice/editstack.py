#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from datetime import datetime
from copy import copy
from cPickle import Pickler, Unpickler
from cStringIO import StringIO
import cherrypy
from cocktail.modeling import ListWrapper, getter, cached_getter
from cocktail.events import Event, EventHub
from cocktail.pkgutils import resolve
from cocktail import schema
from cocktail.controllers import context, get_parameter
from cocktail.persistence import (
    PersistentObject,
    PersistentList, PersistentRelationList,
    PersistentSet, PersistentRelationSet,
    PersistentMapping, PersistentRelationMapping
)
from sitebasis.models import Site


class EditStacksManager(object):
    """A class that manages the loading and persistence of
    L{edit stacks<EditStack>} for the active HTTP session.
    """
    _edit_stack_class = "sitebasis.controllers.backoffice.editstack.EditStack"
    _request_param = "edit_stack"
    _session_key = "sitebasis.controllers.backoffice: preserved_edit_stacks"
    _session_id_key = "sitebasis.controllers.backoffice: edit_stacks_id"
    _persistent_id_prefix = "Persistent"
    __current_edit_stack = None
    
    expiration = 30 * 60 # seconds

    def __init__(self):
        self.__stack_map = {}
 
    def _dumps(self, obj):
        buffer = StringIO()
        pickler = Pickler(buffer)
        pickler.persistent_id = self.__persistent_id
        pickler.dump(obj)
        return buffer.getvalue()

    def __persistent_id(self, obj):
        if isinstance(obj, PersistentObject) and obj.is_inserted:
            return "%s-%s-%s" % (
                self._persistent_id_prefix,
                obj.__class__.full_name,
                obj.id
            )
        else:
            return None

    def _loads(self, data):
        unpickler = Unpickler(StringIO(data))
        unpickler.persistent_load = self.__persistent_load
        return unpickler.load()

    def __persistent_load(self, key):
        if key.startswith(self._persistent_id_prefix):
            parts = key.split("-")
            persistent_type = resolve(parts[1])
            id = int(parts[2])
            return persistent_type.get_instance(id)
        else:
            raise ValueError("Wrong persistent id: " + key)
    
    @cached_getter
    def edit_stacks(self):
        """Obtains a mapping containing all the edit stacks for the current
        browsing session.

        @return: The mapping of stacks, indexed by their numerical id.
        @rtype: mapping of int => L{EditStack}
        """
        preserved_stacks = cherrypy.session.get(self._session_key)
        edit_stacks = {}
        
        if preserved_stacks:
            for id, entry in preserved_stacks.iteritems():
                try:
                    stack = self_get_edit_stack(id)
                except EditStackExpiredError:
                    pass
                else:
                    edit_stacks[id] = stack
        
        return DictWrapper(edit_stacks)

    def _get_edit_stack(self, stack_id,
        preserved_stacks = None,
        current_time = None):

        edit_stack = self.__stack_map.get(stack_id)

        if edit_stack is None:

            if preserved_stacks is None:
                preserved_stacks = cherrypy.session.get(self._session_key)

            if self.expiration and current_time is None:
                current_time = datetime.now()

            if preserved_stacks:

                if self.expiration is not None:
                    now = datetime.now()

                entry = preserved_stacks.get(stack_id)

                if entry is None:
                    raise KeyError("Edit stack %s not found" % stack_id)

                last_update, stack_data = entry

                if self.expiration is not None \
                and (current_time - last_update).seconds >= self.expiration:
                    raise EditStackExpiredError()
                            
                edit_stack = self._loads(stack_data)
                self.__stack_map[stack_id] = edit_stack
            
        return edit_stack
        
    def _get_current_edit_stack(self):
        if self.__current_edit_stack is None:
            self.__current_edit_stack = self.request_edit_stack

        return self.__current_edit_stack

    def _set_current_edit_stack(self, edit_stack):
        self.__current_edit_stack = edit_stack

    current_edit_stack = property(
        _get_current_edit_stack,
        _set_current_edit_stack,
        doc = """The edit stack that applies to the current context.

        @return: The current edit stack.
        @rtype: L{EditStack}
        """)

    @cached_getter
    def request_edit_stack(self):
        """
        Obtains the stack of edit operations for the current HTTP request, as
        indicated by an HTTP parameter.

        @param param: The name of the HTTP parameter that contains the unique
            identifier of the stack to obtain.

        @return: The current edit stack, or None if the "edit_stack" parameter
            is missing.
        @rtype: L{EditStack}

        @raise WrongEditStackError: Raised if the requested edit stack can't be
            found on the session.
        """
        edit_stack = None
        edit_stack_param = get_parameter(
            schema.String(self._request_param, format = r"\d+-\d+"),
            strict = True
        )

        if edit_stack_param:
            id, step = map(int, edit_stack_param.split("-"))
                        
            edit_stack = self._get_edit_stack(id)
    
            # Edit state lost
            if edit_stack is None:
                raise WrongEditStackError(id)

            # Prune the stack
            else:
                while len(edit_stack) > step + 1:
                    edit_stack.pop()                    
        
        return edit_stack

    def create_edit_stack(self):
        """Creates a new edit stack.

        @return: The new edit stack.
        @rtype: L{EditStack}
        """
        edit_stack = resolve(self._edit_stack_class)()
        edit_stack.id = cherrypy.session.get(self._session_id_key, 0)
        cherrypy.session[self._session_id_key] = edit_stack.id + 1
        self.__stack_map[edit_stack.id] = edit_stack
        return edit_stack

    def preserve_edit_stack(self, edit_stack):
        """Stores changes to the given edit stack inside the current HTTP
        session, so it can be retrieved by later requests.
        
        @param edit_stack: The edit stack to preserve.
        @type edit_stack: L{EditStack}
        """
        preserved_stacks = cherrypy.session.get(self._session_key)

        if preserved_stacks is None:
            preserved_stacks = {}
            cherrypy.session[self._session_key] = preserved_stacks

        preserved_stacks[edit_stack.id] = (
            datetime.now(),
            self._dumps(edit_stack)
        )


class EditStack(ListWrapper):
    """A stack describing the context of an edit session. Allows to keep track
    of nested edit operations when dealing with related elements.

    The stack can contain two basic kind of nodes:

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
        node._parent_node = self._items[-1] if self._items else None
        node._stack = self
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
        node = self._items.pop()
        node._stack = None
        node._parent_node = None

    def go(self, index = -1):
        """Redirects the user to the indicated node of the edit stack.

        @param index: The position of the stack to move to.
        @type index: int
        """
        raise cherrypy.HTTPRedirect(self.uri(index))
    
    def uri(self, index = -1):
        """Gets the location of the given position in the stack.
        
        @param index: The position of the stack to get the location for.
        @type index: int

        @return: The URI for the indicated position.
        @rtype: str
        """
        if index < 0:
            index = len(self) + index

        node = self[index]
        
        if isinstance(node, EditNode):
            uri = context["cms"].document_uri(
                "content",
                str(node.item.id) if node.item.is_inserted else "new",
                node.section
            )
        else:
            uri = context["cms"].document_uri("content")

        uri += "?edit_stack=" + self.to_param(index)
        return uri

    def to_param(self, index = -1):
        if index < 0:
            index = len(self) + index

        return "%d-%d" % (self.id, index)


class StackNode(object):
    """Base (abstract) class for the different kinds of nodes that form an
    L{edit stack<EditStack>}.
    """
    __metaclass__ = EventHub
    _stack = None
    _parent_node = None

    @getter
    def stack(self):
        """The edit stack that the node belongs to.
        @type: L{EditStack}
        """
        return self._stack

    @getter
    def parent_node(self):
        """The stack node that the node hangs from.
        @type: L{StackNode}
        """
        return self._parent_node

    def get_ancestor_node(self, node_type):
        """Walks up the edit stack towards its root, looking for the first node
        of the given type.
    
        @param node_type: The type of node to look for.
        @type node_type: L{StackNode} subclass

        @return: The first ancestor of the node of the indicated type, or None
            if the node has no ancestors of that type.
        @rtype: L{StackNode}
        """
        node = self._parent_node
        while node is not None:
            if isinstance(node, node_type):
                break
            node = node._parent_node
        
        return node


class EditNode(StackNode):
    """An L{edit stack<EditStack>} node, used to maintain a set of changes for
    an edited item before they are finally committed.

    @ivar translations: The list of translations defined by the item (note that
        these can change during the course of an edit operation, so that's why
        they are stored in here).
    @type translations: str list 
    """
    _persistent_keys = frozenset([
        "_stack", "_parent_node",
        "_item", "_form_data", "_content_type", "translations",
        "section"
    ])
    _item = None
    translations = None
    section = "fields"

    saving = Event("""
        An event triggered when saving the changes contained within the node,
        just before the transaction is committed.
        """)

    committed = Event("""
        An event triggered after the changes contained within the node have
        been successfully committed to the data store.
        """)
    
    def __init__(self, item):        
        assert item is not None
        self._item = item

    def __getstate__(self):
        state = dict(
            (key, value) for key, value in self.__dict__.iteritems()
            if key in self._persistent_keys
        )
        return state

    @getter
    def content_type(self):
        """The edited content type.
        @type: L{Item<sitebasis.models.Item>} subclass
        """
        return self._item.__class__

    @getter
    def item(self):
        """The edited item.
        @type: L{Item<sitebasis.models.Item>}
        """
        return self._item

    def import_form_data(self, form_data, item):
        """Update the edited item with data gathered from the form."""

        self.form_adapter.import_object(
            form_data,
            item,
            self.form_schema,
            self.content_type
        )
    
    def export_form_data(self, item, form_data):
        """Update the edit form with the data contained on the edited item."""

        self.form_adapter.export_object(
            item,
            form_data,
            self.content_type,
            self.form_schema
        )

        # Default translations
        if self.content_type.translated:
            if not self._item.translations:
                self._item._new_translation(Site.main.default_language)

            self.translations = self._item.translations.keys()
        else:
            self.translations = []

    @cached_getter
    def form_adapter(self):
        """The data adapter used to pass data between the edited item and the
        edit form.
        @type: L{Adapter<cocktail.schema.Adapter>}
        """        
        relation_node = self.get_ancestor_node(RelationNode)
        stack_relation = relation_node and relation_node.member.related_end

        adapter = schema.Adapter()
        adapter.collection_copy_mode = self._adapt_collection
        adapter.exclude([
            member.name
            for member in self.content_type.members().itervalues()
            if not member.editable
            or not member.visible                
            or member is stack_relation
            or (
                isinstance(member, schema.RelationMember)
                and member.related_type
                and not member.related_type.visible
            )
        ])
        return adapter

    def _adapt_collection(self, context, key, value):
        return self._copy_collection(value)

    def _copy_collection(self, collection):

        if isinstance(collection,
        (PersistentList, PersistentRelationList)):
            return list(collection)
        elif isinstance(collection,
        (PersistentMapping, PersistentRelationMapping)):
            return dict(collection.iteritems())
        elif isinstance(collection,
        (PersistentSet, PersistentRelationSet)):
            return set(collection)
        else:
            return copy(collection)

    @cached_getter
    def form_schema(self):
        """The schema that describes the edit form for the edited item.
        @type: L{Schema<cocktail.schema.Schema>}
        """
        form_schema = self.form_adapter.export_schema(self.content_type)
        form_schema.name = "BackOfficeEditForm"
        return form_schema

    @cached_getter
    def form_data(self):
        """The data entered into the edit form."""
 
        # First load: fill the form with data from the edited item
        form_data = {}
        self.export_form_data(self.item, form_data)
        return form_data

    def iter_errors(self):
        """Iterates over the sequence of validation errors produced by the
        current edited state.
        @type: L{ValidationError<cocktail.schema.exceptions.ValidationError>}
            sequence
        """
        return self.form_schema.get_errors(
            self.form_data,
            languages = self.translations,
            persistent_object = self.item
        )

    def iter_changes(self, source = None):
        """Iterates over the set of members that the current edit state has
        modified. Each change is expressed as a tuple containing the affected
        member and language.
        @type: (L{Member<cocktail.schema.Member>}, str) sequence
        """
        source_form_data = {}
        self.form_adapter.export_object(
            source or self._item.draft_source or self._item,
            source_form_data,
            self.content_type,
            self.form_schema
        )

        return schema.diff(
            source_form_data,
            self.form_data,
            self.form_schema
        )

    def member_has_changes(self, member, language = None):
        """Indicates if the node contains changes for the specified member.
        
        @param member: The member to consult.
        @type member: L{Member<cocktail.schema.Member>} or str
 
        @param language: The language for which the comparision is made.
            Only used on translated members; if not provided, the contextual
            language will be used instead.

        @return: True if the specified member has been changed, False
            otherwise.
        @rtype: bool
        """
        if isinstance(member, basestring):
            member = self.content_type[member]

        excluded = object()

        form_value = schema.get(self.form_data, member,
            default = excluded,
            language = language
        )

        if form_value is excluded:
            return False

        base_value = self._item.get(member, language)
        
        if base_value is not None and isinstance(member, schema.Collection):
            base_value = self._copy_collection(base_value)

        return form_value != base_value

    def relate(self, member, item):
        """Adds a relation between the edited item and another item.
        
        @param member: The member describing the relation between the two
            items. It should be the end nearer to the edited item.
        @type member: L{RelationMember<cocktail.schema.RelationMember>}

        @param item: The item to relate.
        @type item: L{Item<sitebasis.models.item.Item>}
        """
        if isinstance(member, schema.Collection):
          
            collection = schema.get(self.form_data, member)
            
            # Editing collections with duplicate entries is not allowed
            if item in collection:
                raise ValueError(
                    "Collections with duplicate entries are not allowed")
           
            schema.add(collection, item)
        else:
            schema.set(self.form_data, member, item)

    def unrelate(self, member, item):
        """Breaks the relation between the edited item and one of its related
        items.
        
        @param member: The member describing the relation between the two
            items. It should be the end nearer to the edited item.
        @type member: L{RelationMember<cocktail.schema.RelationMember>}

        @param item: The item to unrelate.
        @type item: L{Item<sitebasis.models.item.Item>}
        """
        if isinstance(member, schema.Collection):
            collection = schema.get(self.form_data, member)
            schema.remove(collection, item)
        else:
            schema.set(self.form_data, member, None)


class PersistentReference(object):
    """A small utility class, used by L{EditNode} to serialize and unserialize
    references to persistent objects.
    """

    def __init__(self, item):
        self.type = item.__class__
        self.id = item.id


class RelationNode(StackNode):
    """An L{edit stack<EditStack>} node, used to maintain data about an action
    affecting a relation.
    
    @var member: The member describing the relation that is being modified.
    @type member: L{Collection<cocktail.schema.schemacollections.Collection>}
        or L{Reference<cocktail.schema.schemareference.Reference>}
    """
    member = None

    def __getstate__(self):

        state = self.__dict__.copy()        
        member = state.get("member")

        if member:
            state["member"] = member.name

        return state
    
    def __setstate__(self, state):

        member_name = state.pop("member")
        
        for key, value in state.iteritems():            
            setattr(self, key, value)

        content_type = self.get_ancestor_node(EditNode).content_type
        self.member = content_type[member_name]


class EditStackExpiredError(Exception):
    """An exception raised to signal that an edit stack stored on the session
    has expired.
    """


class WrongEditStackError(Exception):
    """An exception raised when requesting an edit stack that is not stored on
    the current session.

    @ivar stack_id: The unique identifier for the requested stack.
    @type stack_id: int
    """

    def __init__(self, stack_id):
        Exception.__init__(self, "Can't find edit stack %s" % stack_id)
        self.stack_id = stack_id

