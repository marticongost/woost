#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from warnings import warn
from datetime import datetime
from copy import copy
from cPickle import Pickler, Unpickler
from cStringIO import StringIO
from itertools import chain
import cherrypy
from cocktail.modeling import (
    getter,
    cached_getter,
    abstractmethod,
    ListWrapper,
    OrderedSet
)
from cocktail.events import Event, EventHub, event_handler
from cocktail.pkgutils import resolve
from cocktail import schema
from cocktail.translations import translations, iter_language_chain
from cocktail.controllers import (
    context,
    get_parameter,
    session,
    request_property
)
from cocktail.persistence import (
    PersistentObject,
    PersistentList, PersistentRelationList,
    PersistentSet, PersistentRelationSet,
    PersistentMapping, PersistentRelationMapping,
    PersistentOrderedSet, PersistentRelationOrderedSet
)
from woost import app
from woost.models import (
    Configuration,
    Item,
    Change,
    Block,
    CreatePermission,
    ReadPermission,
    ModifyPermission,
    DeletePermission,
    ReadMemberPermission,
    ModifyMemberPermission,
    ReadTranslationPermission
)
from woost.models.blockutils import add_block
from woost.controllers.notifications import Notification


class EditStacksManager(object):
    """A class that manages the loading and persistence of
    L{edit stacks<EditStack>} for the active HTTP session.
    """
    _edit_stack_class = "woost.controllers.backoffice.editstack.EditStack"
    _request_param = "edit_stack"
    _session_key = "woost.controllers.backoffice: preserved_edit_stacks"
    _session_id_key = "woost.controllers.backoffice: edit_stacks_id"
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

            full_name = obj.__class__.full_name
            if isinstance(full_name, unicode):
                full_name = str(full_name)

            return "%s-%s-%s" % (
                self._persistent_id_prefix,
                full_name,
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
        preserved_stacks = session.get(self._session_key)
        edit_stacks = {}

        if preserved_stacks:
            for id, entry in preserved_stacks.iteritems():
                stack = self._get_edit_stack(id)
                edit_stacks[id] = stack

        return DictWrapper(edit_stacks)

    def _get_edit_stack(self, stack_id, preserved_stacks = None):

        edit_stack = self.__stack_map.get(stack_id)

        if edit_stack is None:

            if preserved_stacks is None:
                preserved_stacks = session.get(self._session_key)

            if preserved_stacks:

                entry = preserved_stacks.get(stack_id)

                if entry is None:
                    raise WrongEditStackError(stack_id)

                last_update, stack_data = entry

                if self.expiration is not None:
                    preserved_stacks[stack_id] = (
                        datetime.now(),
                        stack_data
                    )

                edit_stack = self._loads(stack_data)
                self.__stack_map[stack_id] = edit_stack

        self._remove_expired_edit_stacks(preserved_stacks)

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
            schema.String(self._request_param, format = r"\d+-\d+")
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
        edit_stack.id = session.get(self._session_id_key, 0)
        edit_stack.root_url = cherrypy.request.params.get("root_url")
        session[self._session_id_key] = edit_stack.id + 1
        self.__stack_map[edit_stack.id] = edit_stack

        self._remove_expired_edit_stacks()

        return edit_stack

    def preserve_edit_stack(self, edit_stack):
        """Stores changes to the given edit stack inside the current HTTP
        session, so it can be retrieved by later requests.

        @param edit_stack: The edit stack to preserve.
        @type edit_stack: L{EditStack}
        """
        preserved_stacks = session.get(self._session_key)

        if preserved_stacks is None:
            preserved_stacks = {}
            session[self._session_key] = preserved_stacks

        preserved_stacks[edit_stack.id] = (
            datetime.now(),
            self._dumps(edit_stack)
        )

        session.save()

    def _remove_expired_edit_stacks(
        self,
        preserved_stacks = None,
        current_time = None
    ):
        if self.expiration is None:
            return

        if preserved_stacks is None:
            preserved_stacks = session.get(self._session_key)

        if preserved_stacks is None:
            return

        if current_time is None:
            current_time = datetime.now()

        for stack_id, (last_update, stack_data) in preserved_stacks.items():
            if (current_time - last_update).seconds >= self.expiration:
                del preserved_stacks[stack_id]

        session.save()


class EditStack(ListWrapper):
    """A stack describing the context of an edit session. Allows to keep track
    of nested edit operations when dealing with related elements.

    The stack can contain several kind of nodes, the most prominent being edit
    and relation nodes:

        * L{edit nodes<EditNode>} are associated with a single
          L{item<woost.models.items.Item>}, and store all the changes
          performed on it before they are finally saved.

        * L{relation nodes<RelationNode>} indicate a nested edit operation on a
          related item or set of items.

    @ivar id: A numerical identifier for the stack. It is guaranteed to be
        unique throughout the current browser session.
    """
    id = None
    root_url = None

    def push(self, node):
        """Adds a new node to the edit stack.

        @param node: The node to add.
        @type node: L{StackNode},
            L{collection<cocktail.schema.schemacollections.Collection>}
            or L{relation<cocktail.schema.schemarelations.Relation>}
        """
        node._parent_node = self._items[-1] if self._items else None
        node._stack = self
        node._index = len(self._items)
        self._items.append(node)

    def pop(self):
        """Removes the last node from the stack and returns it.

        @return: The last node of the stack.
        @rtype: L{StackNode},
            L{collection<cocktail.schema.schemacollections.Collection>}
            or L{relation<cocktail.schema.schemarelations.Relation>}

        @raise IndexError: Raised when trying to pop a node from an empty
            stack.
        """
        node = self._items.pop()
        node._stack = None
        node._index = None
        node._parent_node = None

    def go_back(self, **params):
        """Redirects the user to the parent of the topmost node in the stack.

        If the root of the stack is reached or surpassed, the user will be
        redirected to the application's root.

        @param params: Additional query string parameters to pass to the
            destination URI.
        """
        if len(self._items) > 1:

            target_node = self._items[-2]
            if isinstance(target_node, RelationNode):
                target_node = self._items[-3]

            back_hash = target_node.back_hash(self._items[-1])
            uri = target_node.uri(**params)
            if back_hash:
                uri += "#" + back_hash

            raise cherrypy.HTTPRedirect(uri)
        else:
            if self.root_url:
                # When redirecting the user by means of a callback URL, discard
                # all notifications before redirecting, since there is no
                # guarantee that the target URL will display them. This is
                # clearly not ideal, but the alternative (having them stack up
                # and show all at once whenever the user opens the backoffice)
                # is not that great either.
                Notification.pop()
                raise cherrypy.HTTPRedirect(self.root_url)
            else:
                raise cherrypy.HTTPRedirect(
                    context["cms"].contextual_uri(**params)
                )

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
        warn(
            "edit_stack.uri(n) is deprecated, use edit_stack[n].uri() instead",
            DeprecationWarning,
            stacklevel = 2
        )

        if index < 0:
            index = len(self) + index

        return self[index].uri()

    def to_param(self, index = -1):
        if index < 0:
            index = len(self) + index

        return "%d-%d" % (self.id, index)

    def remove_references(self, removed_items):
        """Removes all references to the indicated items from the edit stack.

        @param removed_items: The items to remove from the stack.
        @type removed_items: L{Item<woost.models.item.Item>} sequence
        """
        # For each edit node in the stack
        for i, node in enumerate(self):
            if isinstance(node, EditNode):

                # Truncate the node and the rest of the stack if the node was
                # editing a deleted item
                if node.item in removed_items:
                    while self[-1] is not node:
                        self.pop()
                    self.pop()
                    break

                # Find all relations to persistent items
                form_data = node.form_data

                for key, member in node.item.__class__.members().iteritems():
                    if isinstance(member, schema.RelationMember) \
                    and member.is_persistent_relation:

                        # Clean up references (set to None)
                        if isinstance(member, schema.Reference) \
                        and form_data.get(key) in removed_items:
                            form_data[key] = None

                        # Clean up collections (completely remove the indicated
                        # items)
                        elif isinstance(member, schema.Collection):

                            items = form_data.get(key)
                            if items:
                                for item in removed_items:
                                    while True:
                                        try:
                                            schema.remove(items, item)
                                        except:
                                            break


class StackNode(object):
    """Base (abstract) class for the different kinds of nodes that form an
    L{edit stack<EditStack>}.
    """
    __metaclass__ = EventHub
    _stack = None
    _parent_node = None
    _index = None

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

    @getter
    def index(self):
        """Gets the position of the node in its stack.
        @type: int
        """
        return self._index

    def get_ancestor_node(self, node_type, include_self = False):
        """Walks up the edit stack towards its root, looking for the first node
        of the given type.

        @param node_type: The type of node to look for.
        @type node_type: L{StackNode} subclass

        @return: The first ancestor of the node of the indicated type, or None
            if the node has no ancestors of that type.
        @rtype: L{StackNode}
        """
        node = self if include_self else self._parent_node
        while node is not None:
            if isinstance(node, node_type):
                break
            node = node._parent_node

        return node

    @abstractmethod
    def uri(self, **params):
        """Gets the URI for the stack node.

        @param params: Additional query string parameters to include in the
            produced URI.

        @return: The URI for the node.
        @rtype: unicode
        """

    def back_hash(self, previous_node):
        return None

    def push_to_stack(self, edit_stack = None):
        edit_stacks_manager = context["edit_stacks_manager"]

        if edit_stack is None:
            edit_stack = edit_stacks_manager.current_edit_stack
            if edit_stack is None:
                edit_stack = edit_stacks_manager.create_edit_stack()
                edit_stacks_manager.current_edit_stack = edit_stack

        edit_stack.push(self)
        edit_stacks_manager.preserve_edit_stack(edit_stack)
        edit_stack.go()


class EditNode(StackNode):
    """An L{edit stack<EditStack>} node, used to maintain a set of changes for
    an edited item before they are finally committed.

    @ivar item_translations: A list of locale codes indicating the translations
        defined by the edited item in this edit session. Note that this can
        differ from the list defined by the item in the database, since users
        are able to add / delete translations during the edit operation.
    @type item_translations: str set

    @ivar visible_translations: A list of locale codes indicating the
        translations that are included in the edit operation. This will always
        be a subset of L{item_translations}. Translations not included in this
        subset will not be included in the edit form, and they will be left
        untouched when the item is finally saved.
    @type visible_translations: str set
    """
    _persistent_keys = frozenset([
        "_stack",
        "_parent_node",
        "_index",
        "_item",
        "item_id",
        "form_data",
        "item_translations",
        "visible_translations",
        "section",
        "tab"
    ])
    _item = None
    item_translations = None
    visible_translations = None
    section = "fields"
    tab = None
    verbose_member_mode = False

    saving = Event("""
        An event triggered when saving the changes contained within the node,
        after loading form data to the modified item and before the transaction
        is committed.

        @ivar user: The user that makes the changes.
        @type user: L{User<woost.models.User>}

        @ivar item: The item being saved.
        @type item: L{Item<woost.models.Item>}

        @ivar is_new: Indicates if the item is being created (True) or modified
            (False).
        @type is_new: bool

        @ivar changeset: The change set describing the changes.
        @type changeset: L{ChangeSet<woost.models.ChangeSet>}
        """)

    committed = Event("""
        An event triggered after the changes contained within the node have
        been successfully committed to the data store.

        @ivar user: The user that makes the changes.
        @type user: L{User<woost.models.User>}

        @ivar changeset: The change set describing the changes.
        @type changeset: L{ChangeSet<woost.models.ChangeSet>}
        """)

    def __init__(self, item, visible_translations = None):
        self._item = item

        if item.__class__.translated:

            if visible_translations is None:
                visible_translations = item.translations
            else:
                if item.is_inserted:
                    visible_translations = [
                        language
                        for language in visible_translations
                        if language in item.translations
                    ]
                else:
                    for language in visible_translations:
                        item.new_translation(language)

            self.item_translations = set(item.translations)

            user = app.user
            self.visible_translations = set(
                language
                for language in visible_translations
                if user.has_permission(
                    ReadTranslationPermission,
                    language = language
                )
            )
        else:
            self.item_translations = None
            self.visible_translations = None

        self.item_id = item.require_id()
        self.form_data = {}
        self.export_form_data(item, self.form_data)

    def __translate__(self, language, **kwargs):
        if self.item.is_inserted:
            return translations(self.item)
        else:
            return translations("creating", content_type = self.content_type)

    def uri(self, **params):

        if "edit_stack" not in params:
            params["edit_stack"] = self.stack.to_param(self.index)

        uri = context["cms"].contextual_uri(
            "content",
            str(self.item.id) if self.item.is_inserted or self.item.is_deleted else "new",
            self.section,
            **params
        )

        uri += "#" + (self.tab or "")

        return uri

    def __getstate__(self):

        state = {}

        for key, value in self.__dict__.iteritems():
            if key in self._persistent_keys:
                if key == "_item" and not value.is_inserted:
                    value = None
                state[key] = value

        state["content_type"] = self._item.__class__
        return state

    def __setstate__(self, state):

        content_type = state.pop("content_type", None)

        for key, value in state.iteritems():
            if key in self._persistent_keys:
                if key == "_item":
                    if value is None:
                        value = content_type()
                        value.id = self.item_id
                        if content_type.translated:
                            for language in state["visible_translations"]:
                                value.new_translation(language)

                setattr(self, key, value)

    @getter
    def content_type(self):
        """The edited content type.
        @type: L{Item<woost.models.Item>} subclass
        """
        return self._item.__class__

    @getter
    def item(self):
        """The edited item.
        @type: L{Item<woost.models.Item>}
        """
        return self._item

    def import_form_data(self, form_data, item):
        """Update the edited item with data gathered from the form."""

        self.form_adapter.import_object(
            form_data,
            item,
            self.form_schema,
            self.content_type,
            languages = self.item_translations
        )

        # Drop deleted translations
        if item.__class__.translated:
            user = app.user

            deleted_translations = (
                set(
                    language
                    for language in item.translations
                    if user.has_permission(
                        ReadTranslationPermission,
                        language = language
                    )
                )
                - self.item_translations
            )

            for language in deleted_translations:
                del item.translations[language]

    def export_form_data(self, item, form_data):
        """Update the edit form with the data contained on the edited item."""
        self.form_adapter.export_object(
            item,
            form_data,
            self.content_type,
            self.form_schema
        )

    @cached_getter
    def form_adapter(self):
        """The data adapter used to pass data between the edited item and the
        edit form.
        @type: L{Adapter<cocktail.schema.Adapter>}
        """
        adapter = schema.Adapter()
        adapter.collection_copy_mode = self._adapt_collection
        adapter.implicit_copy = False

        for member in self.content_type.iter_members():
            mode = self.get_member_edit_mode(member)
            if mode == schema.EDITABLE:
                adapter.copy(
                    member.name,
                    properties =
                        None
                        if member.editable == schema.EDITABLE
                        else {"editable": schema.EDITABLE}
                )
            elif mode == schema.READ_ONLY:
                adapter.export_read_only(member.name)

        return adapter

    def get_member_edit_mode(self, member):

        if self.verbose_member_mode:
            from cocktail.styled import styled
            print "Member mode for",
            print styled(member.name, style = "bold"),
            print "is",

        if member.editable == schema.NOT_EDITABLE:
            if self.verbose_member_mode:
                print styled("NOT_EDITABLE", "magenta", style = "bold")
                print styled("(specified by the member)\n", "pink")
            return schema.NOT_EDITABLE

        if not member.visible:
            if self.verbose_member_mode:
                print styled("NOT_EDITABLE", "magenta", style = "bold")
                print styled("(not visible)\n", "pink")
            return schema.NOT_EDITABLE

        # Hide relations with relation nodes in the stack
        relation_node = self.get_ancestor_node(RelationNode)
        if relation_node and member is relation_node.member.related_end:
            if self.verbose_member_mode:
                print styled("NOT_EDITABLE", "magenta", style = "bold")
                print styled("(relation in stack)\n", "pink")
            return schema.NOT_EDITABLE

        user = app.user

        if (
            self.item
            and self.item.is_inserted
            and isinstance(member, schema.RelationMember)
            and member.bidirectional and member.related_end.integral
        ):
            if self.verbose_member_mode:
                print styled("READ_ONLY", "yellow", style = "bold")
                print styled("(integral related end)\n", "pink")
            return schema.READ_ONLY

        if not user.has_permission(ReadMemberPermission, member = member):
            if self.verbose_member_mode:
                print styled("NOT_EDITABLE", "magenta", style = "bold")
                print styled("(not authorized to read this member)\n", "pink")
            return schema.NOT_EDITABLE

        if not user.has_permission(ModifyMemberPermission, member = member):
            if self.verbose_member_mode:
                print styled("READ_ONLY", "yellow", style = "bold")
                print styled(
                    "(not authorized to modify this member)\n",
                    "pink"
                )
            return schema.READ_ONLY

        if isinstance(member, schema.RelationMember) \
        and member.is_persistent_relation:

            # Hide relations to invisible types
            if not member.related_type.visible:
                if self.verbose_member_mode:
                    print styled("NOT_EDITABLE", "magenta", style = "bold")
                    print styled("(related type is invisible)\n", "pink")
                return schema.NOT_EDITABLE

            # Hide empty collections with the exclude_when_empty flag
            # set
            if (
                isinstance(member, schema.Collection)
                and member.exclude_when_empty
                and not member.select_constraint_instances(
                    parent = self.item
                )
            ):
                if self.verbose_member_mode:
                    print styled("NOT_EDITABLE", "magenta", style = "bold")
                    print styled("(exclude empty collection)\n", "pink")
                return schema.NOT_EDITABLE

            def class_family_permission(root, permission_type):
                return any(
                    user.has_permission(permission_type, target = cls)
                    for cls in root.schema_tree()
                )

            # Require read permission for related types
            if not class_family_permission(
                member.related_type, ReadPermission
            ):
                if self.verbose_member_mode:
                    print styled("NOT_EDITABLE", "magenta", style = "bold")
                    print styled(
                        "(not authorized to read related type)\n",
                        "pink"
                    )
                return schema.NOT_EDITABLE

            # Integral relation
            if (
                isinstance(member, schema.Reference)
                and member.integral
                and self.item
            ):
                # Empty: require create permission
                # Has an item: require edit or delete permission
                if self.item.get(member) is None:
                    if not class_family_permission(
                        member.type,
                        CreatePermission
                    ):
                        if self.verbose_member_mode:
                            print styled("READ_ONLY", "yellow", style = "bold")
                            print styled(
                                "(can't create integral component)\n",
                                "pink"
                            )
                        return schema.READ_ONLY
                elif not (
                    class_family_permission(
                        member.type, ModifyPermission
                    )
                    and class_family_permission(
                        member.type, DeletePermission
                    )
                ):
                    if self.verbose_member_mode:
                        print styled("READ_ONLY", "yellow", style = "bold")
                        print styled(
                            "(can't modify or delete integral component)\n",
                            "pink"
                        )
                    return schema.READ_ONLY

        # Remove all relations to blocks from the edit view
        if (
            isinstance(member, schema.RelationMember)
            and member.related_type
            and issubclass(member.related_type, Block)
        ):
            if self.verbose_member_mode:
                print styled("NOT_EDITABLE", "magenta", style = "bold")
                print styled("(is a block slot)\n", "pink")
            return schema.NOT_EDITABLE

        if not user.has_permission(ModifyPermission, target = self.item):
            if self.verbose_member_mode:
                print styled("READ_ONLY", "yellow", style = "bold")
                print styled("(not authorized to modify this object)\n", "pink")
            return schema.READ_ONLY

        if self.verbose_member_mode:
            if member.editable == schema.EDITABLE:
                print styled("EDITABLE\n", "bright_green", style = "bold")
            elif member.editable == schema.READ_ONLY:
                print styled("READ_ONLY", "yellow", style = "bold")
                print styled("(specified by the member)\n", "pink")

        return member.editable

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
        (PersistentOrderedSet, PersistentRelationOrderedSet)):
            return OrderedSet(collection)
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

    def iter_errors(self):
        """Iterates over the sequence of validation errors produced by the
        current edited state.
        @type: L{ValidationError<cocktail.schema.exceptions.ValidationError>}
            sequence
        """
        return self.form_schema.get_errors(
            self.form_data,
            languages = self.item_translations,
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
            source or self._item,
            source_form_data,
            self.content_type,
            self.form_schema
        )
        return schema.diff(
            source_form_data,
            self.form_data,
            self.form_schema,
            exclude = lambda member: member.editable != schema.EDITABLE
        )

    def relate(self, member, item):
        """Adds a relation between the edited item and another item.

        @param member: The member describing the relation between the two
            items. It should be the end nearer to the edited item.
        @type member: L{RelationMember<cocktail.schema.RelationMember>}

        @param item: The item to relate.
        @type item: L{Item<woost.models.item.Item>}
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
        @type item: L{Item<woost.models.item.Item>}
        """
        if isinstance(member, schema.Collection):
            collection = schema.get(self.form_data, member)
            schema.remove(collection, item)
        else:
            schema.set(self.form_data, member, None)

    def item_saved_notification(self, is_new, change):
        """Notifies the user that the node's item has been saved.

        @param is_new: Indicates if the save operation consisted of an
            insertion (True) or an update of an existing item (False).
        @type is_new: bool

        @param change: A change object describing the save operation.
        @type change: L{Change<woost.models.changeset.Change>}
        """
        notification = self.create_item_saved_notification(is_new, change)
        if notification is not None:
            notification.emit()

    def create_item_saved_notification(self, is_new, change):
        return ItemSavedNotification(self.item, is_new, change)

    def add_translation(self, language):

        if language in self.item_translations:
            return

        self.item_translations.add(language)
        self.visible_translations.add(language)
        form_data = self.form_data

        # Try to copy an existing fallback translation
        for fallback_language in iter_language_chain(
            language,
            include_self = False
        ):
            if fallback_language in self.item_translations:
                for key, member \
                in self.form_schema.members().iteritems():
                    if member.translated:
                        value = schema.get(
                            form_data,
                            key,
                            language = fallback_language
                        )
                        schema.set(
                            form_data,
                            key,
                            value,
                            language = language
                        )
                break
        # If there's no fallback translation to use, create a new
        # translation from scratch
        else:
            translation_data = {}
            translation_type = self.content_type.translation
            translation_type.init_instance(translation_data)

            for key, value in translation_data.iteritems():
                schema.set(
                    form_data,
                    key,
                    value,
                    language = language
                )

    def remove_translation(self, language):

        self.item_translations.discard(language)
        self.visible_translations.discard(language)
        form_data = self.form_data

        for key, member in self.form_schema.members().iteritems():
            if member.translated:
                values = form_data.get(key)
                if values:
                    values.pop(language, None)


class SelectionNode(StackNode):
    """An L{edit stack<EditStack>} node representing an item selection dialog.

    @var content_type: The type of item to select.
    @type content_type: L{Item<woost.models.item.Item>} subclass

    @var selection_parameter: The name of the HTTP parameter used to forward
        the selected item to the stack's parent node once the user confirms its
        choice.
    @type selection_parameter: str
    """
    content_type = None
    selection_parameter = None

    def __translate__(self, language, **kwargs):
        return translations(
            "woost.views.BackOfficeLayout edit stack select",
            relation = self.parent_node and self.parent_node.member,
            type = self.content_type
        )

    def uri(self, **params):

        if "edit_stack" not in params:
            params["edit_stack"] = self.stack.to_param(self.index)

        params.setdefault("type", self.content_type.full_name)
        return context["cms"].contextual_uri("content", **params)


class RelationNode(StackNode):
    """An L{edit stack<EditStack>} node, used to maintain data about an action
    affecting a relation.

    @var member: The member describing the relation that is being modified.
    @type member: L{Collection<cocktail.schema.schemacollections.Collection>}
        or L{Reference<cocktail.schema.schemareference.Reference>}
    """
    member = None

    def __translate__(self, language, **kwargs):
        if isinstance(self.member, schema.Collection):
            return translations(
                "woost.views.BackOfficeLayout edit stack add",
                relation = self.member
            )
        else:
            return translations(
                "woost.views.BackOfficeLayout edit stack select",
                relation = self.member
            )

    def uri(self, **params):

        if "edit_stack" not in params:
            params["edit_stack"] = self.stack.to_param(self.index)

        return context["cms"].contextual_uri("content", **params)

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


class EditBlocksNode(StackNode):

    item = None

    def __getstate__(self):
        return {
            "_stack": self._stack,
            "_parent_node": self._parent_node,
            "_index": self._index,
            "item": self.item.id
        }

    def __setstate__(self, state):
        self._stack = state["_stack"]
        self._parent_node = state["_parent_node"]
        self._index = state["_index"]
        self.item = Item.require_instance(state["item"])

    def uri(self, **params):

        if "edit_stack" not in params:
            params["edit_stack"] = self.stack.to_param(self.index)

        return context["cms"].contextual_uri(
            "blocks",
            str(self.item.id),
            **params
        )

    def back_hash(self, previous_node):
        if isinstance(previous_node, EditNode):
            return "block" + str(previous_node.item.id)


class AddBlockNode(EditNode):

    block_parent = None
    block_slot = None
    block_positioning = "append"
    block_anchor = None

    _persistent_keys = EditNode._persistent_keys | frozenset(["block_positioning"])

    def __getstate__(self):
        state = EditNode.__getstate__(self)
        state["block_parent"] = self.block_parent.id
        state["block_slot"] = self.block_slot.name

        if self.block_anchor is not None:
            state["block_anchor"] = self.block_anchor.id
        else:
            state["block_anchor"] = None

        return state

    def __setstate__(self, state):

        EditNode.__setstate__(self, state)

        self.block_parent = Item.get_instance(state["block_parent"])

        if self.block_parent:
            block_type = type(self.block_parent)
            self.block_slot = block_type.get_member(state["block_slot"])

        anchor_id = state.get("block_anchor")
        if anchor_id is not None:
            self.block_anchor = Block.get_instance(anchor_id)

    @event_handler
    def handle_saving(cls, e):
        node = e.source
        add_block(
            node.item,
            node.block_parent,
            node.block_slot,
            positioning = node.block_positioning,
            anchor = node.block_anchor
        )


class WrongEditStackError(Exception):
    """An exception raised when requesting an edit stack that is not stored on
    the current session.

    @ivar stack_id: The unique identifier for the requested stack.
    @type stack_id: int
    """

    def __init__(self, stack_id):
        Exception.__init__(self, "Can't find edit stack %s" % stack_id)
        self.stack_id = stack_id


class ItemSavedNotification(Notification):
    """A notification displayed when an object is saved using the backoffice
    interface.
    """

    def __init__(self,
        item,
        item_is_new,
        change,
        category = "success",
        transient = False
    ):
        Notification.__init__(
            self,
            category = category,
            transient = transient
        )
        self.__item_id = item.id
        self.__item_is_new = item_is_new
        self.__change_id = None if change is None else change.id

    @property
    def item(self):
        return Item.get_instance(self.__item_id)

    @property
    def item_is_new(self):
        return self.__item_is_new

    @request_property
    def change(self):
        return self.__change_id and Change.get_instance(self.__change_id)

