#-*- coding: utf-8 -*-
u"""
Declaration of back office actions.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from threading import Lock
from urllib import unquote
from cocktail.modeling import getter, ListWrapper
from cocktail.translations import translations, get_language
from cocktail.pkgutils import resolve, get_full_name
from cocktail.persistence import datastore, transactional
from cocktail.controllers import (
    view_state,
    context as controller_context,
    request_property,
    get_parameter,
    session,
    redirect,
    get_request_url_builder
)
from cocktail import schema
from cocktail.html import templates
from woost import app
from woost.models import (
    Configuration,
    Item,
    SiteInstallation,
    Publishable,
    Document,
    URI,
    File,
    Block,
    ReadPermission,
    ReadMemberPermission,
    CreatePermission,
    ModifyPermission,
    DeletePermission,
    ModifyMemberPermission,
    ReadHistoryPermission,
    InstallationSyncPermission
)
from woost.models.blockutils import (
    add_block,
    type_is_block_container,
    schema_tree_has_block_container
)
from woost.controllers.notifications import Notification
from woost.controllers.backoffice.editstack import (
    EditNode,
    SelectionNode,
    RelationNode,
    EditBlocksNode
)

# User action model declaration
#------------------------------------------------------------------------------

# Class stub (needed by the metaclass)
UserAction = None

_action_list = ListWrapper([])
_action_map = {}
_registration_lock = Lock()

def get_user_action(id):
    """Gets a user action, given its unique identifier.

    @param id: The unique identifier of the action to obtain.
    @type id: str

    @return: The requested user action, or None if not defined.
    @rtype: L{UserAction}
    """
    return _action_map.get(id)

def get_user_actions(**kwargs):
    """Returns a collection of all actions registered with the site.

    @return: The list of user actions.
    @rtype: iterable L{UserAction} sequence
    """
    return _action_list

def get_view_actions(context, target = None):
    """Obtains the list of actions that can be displayed on a given view.

    @param context: A set of string identifiers, such as "context_menu",
        "toolbar", etc. Different views can make use of as many different
        identifiers as they require.
    @type container: str set

    @param target: The item or content type affected by the action.
    @type target: L{Item<woost.models.item.Item>} instance or class

    @return: The list of user actions available under the specified context.
    @rtype: iterable L{UserAction} sequence
    """
    return (
        action
        for action in _action_list
        if action.enabled and action.is_available(context, target)
    )

def export_user_actions(element, context, target):
    element["data-woost-available-actions"] = " ".join(
        action.id
        for action in get_view_actions(context, target)
    )


class UserAction(object):
    """An action that is made available to users at the backoffice
    interface. The user actions model allows site implementors to extend the
    site with their own actions, or to disable or override standard actions
    with fine grained control of their context.

    @ivar enabled: Controls the site-wide availavility of the action.
    @type enabled: bool

    @ivar included: A set of context identifiers under which the action is
        made available. Entries on the sequence are joined using a logical OR.
        Entries can also consist of a tuple of identifiers, which will be
        joined using a logical AND operation.
    @type included: set(str or tuple(str))

    @ivar excluded: A set of context identifiers under which the action won't
        be made available. Identifiers are specified using the same format used
        by the L{included} parameter. If both X{included} and X{excluded} are
        specified, both conditions will be tested, with X{excluded} carrying
        more weight.
    @type excluded: set(str or tuple(str))

    @ivar content_type: When set, the action will only be made available to the
        indicated content type or its subclasses.
    @type content_type: L{Item<woost.models.Item>} subclass

    @ivar excluded_content_types: A set of content types that the action should
        never match (ie. execptions to the `content_type` property).
    @type excluded_content_types: set of L{Item<woost.models.Item>} subclasses

    @ivar ignores_selection: Set to True for actions that don't operate on a
        selection of content.
    @type ignores_selection: bool

    @ivar min: The minimum number of content items that the action can be
        invoked on. Setting it to 0 or None disables the constraint.
    @type min: int

    @ivar max: The maximum number of content items that the action can be
        invoked on. A value of None disables the constraint.
    @type max: int

    @ivar direct_link: Set to True for actions that can provide a direct URL
        for their execution, without requiring a form submit and redirection.
    @type direct_link: bool
    """
    enabled = True
    included = frozenset(["toolbar", "item_buttons"])
    excluded = frozenset([
        "selector",
        "calendar_content_view",
        "changelog"
    ])
    content_type = None
    excluded_content_types = None
    ignores_selection = False
    min = 1
    max = 1
    direct_link = False
    link_target = None
    show_as_primary_action = "never"
    hidden_when_disabled = False

    def __init__(self, id):

        if not id:
            raise ValueError("User actions must have an id")

        if not isinstance(id, basestring):
            raise TypeError("User action identifiers must be strings, not %s"
                            % type(id))
        self._id = id
        self.excluded_content_types = set()

    @getter
    def id(self):
        """The unique identifier for the action.
        @type: str
        """
        return self._id

    def register(self, before = None, after = None):
        """Registers the action with the site, so that it can appear on action
        containers and be handled by controllers.

        Registering an action with an identifier already in use is allowed, and
        will override the previously registered action.

        @param before: Indicates the position for the registered action. Should
            match the identifier of an already registered action. The new
            action will be inserted immediately before the indicated action.
        @type before: str

        @param after: Indicates the position for the registered action. Should
            match the identifier of an already registered action. The new
            action will be inserted immediately after the indicated action.
        @type after: str

        @raise ValueError: Raised if both L{before} and L{after} are set.
        @raise ValueError: Raised if the position indicated by L{after} or
            L{before} can't be found.
        """
        if after and before:
            raise ValueError("Can't combine 'after' and 'before' parameters")

        with _registration_lock:
            prev_action = get_user_action(self._id)

            if after or before:
                if prev_action:
                    _action_list._items.remove(prev_action)

                ref_action = _action_map[after or before]
                pos = _action_list.index(ref_action)

                if before:
                    _action_list._items.insert(pos, self)
                else:
                    _action_list._items.insert(pos + 1, self)

            elif prev_action:
                pos = _action_list.index(prev_action)
                _action_list._items[pos] = self
            else:
                _action_list._items.append(self)

            _action_map[self._id] = self

    def unregister(self):
        with _registration_lock:
            try:
                _action_list._items.remove(self)
                _action_map[self._id]
            except (KeyError, ValueError):
                raise ValueError(
                    "Can't unregister action %r; it is not registered",
                    self
                )

    def is_primary(self, target, context):
        if self.show_as_primary_action == "always":
            return True
        elif self.show_as_primary_action == "never":
            return False
        elif self.show_as_primary_action == "on_content_type":
            if isinstance(target, type):
                return self.matches_content_type(
                    target,
                    accept_ancestors = False
                )
            else:
                return True
        else:
            raise ValueError(
                "%r has an invalid 'show_as_primary_action' attribute: "
                "expected one of 'always', 'never' or 'on_content_type', "
                "got %r instead"
                % (self, self.show_as_primary_action)
            )

    def matches_context(self, context):
        """Indicates if the action is available under a certain context.

        @param context: A set of string identifiers, such as "context_menu",
            "toolbar", etc. Different views can make use of as many different
            identifiers as they require.
        @type container: str set

        @return: True if the action can be shown in the given context, False
            otherwise.
        @rtype: bool
        """
        def match(tokens):
            for token in tokens:
                if isinstance(token, str):
                    if token in context:
                        return True
                elif context.issuperset(token):
                    return True
            return False

        if self.included and not match(self.included):
            return False

        if self.excluded and match(self.excluded):
            return False

        return True

    def matches_content_type(self, target, accept_ancestors = True):
        """Indicates if the action applies to the indicated type.

        @param target: The instance or class to evaluate.
        @type target: L{Item<woost.models.item.Item>} instance or class

        @param accept_ancestors: Indicates if an acestor type for the action's
            stated content type should match. For example, if set to True,
            a listing of type Item will match all actions.

        @return: True if the action is applicable to the given content type,
            False otherwise.
        @rtype: bool
        """
        if self.excluded_content_types:
            excluded_types = tuple(self.excluded_content_types)
            if isinstance(target, type):
                if issubclass(target, excluded_types):
                    return False
            elif isinstance(target, excluded_types):
                return False

        if self.content_type is None:
            return True

        if isinstance(target, type):

            # Listing / editing a type derived from the action's type
            if issubclass(target, self.content_type):
                return True

            # Listing / editing an ancestor type for the action's type
            if accept_ancestors:
                if isinstance(self.content_type, type):
                    if issubclass(self.content_type, target):
                        return True
                else:
                    for content_type in self.content_type:
                        if issubclass(content_type, target):
                            return True

        # Listing / editing an instance of the action's type
        elif isinstance(target, self.content_type):
            return True

        return False

    def is_available(self, context, target):
        """Indicates if the action is available for the indicated target and
        user.

        @param target: The item or content type affected by the action.
        @type target: L{Item<woost.models.item.Item>} instance or class

        @return: True if the action is applicable to the given target and can
            be executed by the given user.
        @rtype: bool
        """
        return (
            self.matches_context(context)
            and self.matches_content_type(target)
            and self.is_permitted(app.user, target)
        )

    def is_permitted(self, user, target):
        """Determines if the given user is allowed to execute the action.

        Subclasses should override this method in order to implement their
        access restrictions.

        @param user: The user to authorize.
        @type user: L{User<woost.models.user.User>}

        @param target: The item or content type affected by the action.
        @type target: L{Item<woost.models.item.Item>} instance or class

        @return: True if the user is granted permission, False otherwise.
        @rtype: bool
        """
        return True

    def get_dropdown_panel(self, action_bar):
        """Produces the user interface fragment that should be shown as the
        content for the action's dropdown panel.

        Returning None indicates the action doesn't have a dropdown panel
        available.

        @param action_bar: The toolbar where the dropdown will be inserted.
        @type action_bar: L{ActionBar<woost.views.ActionBar>}

        @return: The user interface for the action's dropdown panel.
        @rtype: L{Element<cocktail.html.Element>}
        """
        return None

    def get_parameters_schema(self, controller, selection):
        members = self.get_parameter_members(controller, selection)
        if members:
            return schema.Schema(
                get_full_name(self.__class__) + ".schema",
                members = members
            )
        return None

    def get_parameter_members(self, controller, selection):
        return []

    def get_errors(
        self,
        controller,
        selection,
        parameters_schema,
        **parameters
    ):
        """Validates the context of an action before it is invoked.

        @param controller: The controller that invokes the action.
        @type controller: L{Controller<cocktail.controllers.controller.Controller>}

        @param selection: The collection of items that the action will be
            applied to.
        @type selection: L{Item<woost.models.item.Item>} collection

        @return: The list of errors for the indicated context.
        @rtype: iterable L{Exception} sequence
        """
        if not self.ignores_selection:

            # Validate selection size
            selection_size = len(selection) if selection is not None else 0

            if (self.min and selection_size < self.min) \
            or (self.max is not None and selection_size > self.max):
                yield SelectionError(self, selection_size)

            # Validate parameters
            if parameters_schema:
                for error in parameters_schema.get_errors(
                    parameters,
                    action = self,
                    controller = controller,
                    selection = selection
                ):
                    yield error

    def invoke(self, controller, selection, **parameters):
        """Delegates control of the current request to the action. Actions can
        override this method to implement their own response logic; by default,
        users are redirected to an action specific controller.

        @param controller: The controller that invokes the action.
        @type controller: L{Controller<cocktail.controllers.controller.Controller>}
        """
        redirect(self.get_url(controller, selection))

    def get_url(self, controller, selection):
        """Produces the URL of the controller that handles the action
        execution. This is used by the default implementation of the L{invoke}
        method. Actions can override this method to alter this value.

        By default, single selection actions produce an URL of the form
        $cms_base_url/content/$selected_item_id/$action_id. Other actions
        follow the form $cms_base_url/$action_id/?selection=$selection_ids

        @param controller: The controller that invokes the action.
        @type controller: L{Controller<cocktail.controllers.controller.Controller>}

        @param selection: The collection of items that the action is invoked
            on.
        @type selection: L{Item<woost.models.item.Item>} collection

        @return: The URL where the user should be redirected.
        @rtype: str
        """
        params = self.get_url_params(controller, selection)

        if self.ignores_selection:
            return controller.contextual_uri(self.id, **params)

        elif self.min == self.max == 1:
            # Single selection
            return controller.edit_uri(
                    selection[0],
                    self.id,
                    **params)
        else:
            return controller.contextual_uri(
                    self.id,
                    selection = [item.id for item in selection],
                    **params)

    def get_url_params(self, controller, selection):
        """Produces extra URL parameters for the L{get_url} method.

        @param controller: The controller that invokes the action.
        @type controller: L{Controller<cocktail.controllers.controller.Controller>}

        @param selection: The collection of items that the action is invoked
            on.
        @type selection: L{Item<woost.models.item.Item>} collection

        @return: A mapping containing additional parameters to include on the
            URL associated to the action.
        @rtype: dict
        """
        params = {}

        if controller.edit_stack:
            params["edit_stack"] = controller.edit_stack.to_param()

        return params

    @getter
    def icon_uri(self):
        return "/resources/woost/images/%s.png" % self.id


class SelectionError(Exception):
    """An exception produced by the L{UserAction.get_errors} method when an
    action is attempted against an invalid number of items."""

    def __init__(self, action, selection_size):
        Exception.__init__(self, "Can't execute action '%s' on %d item(s)."
            % (action.id, selection_size))
        self.action = action
        self.selection_size = selection_size


# Implementation of concrete actions
#------------------------------------------------------------------------------

class CreateAction(UserAction):

    excluded = UserAction.excluded | frozenset(["existing_only"])
    min = None
    max = None
    ignores_selection = True
    show_as_primary_action = "always"

    def get_parameter_members(self, controller, selection):
        return [
            schema.Reference(
                "type",
                class_family = Item
            )
        ]

    def get_instantiable_types(self, root_type):

        user = app.user
        role = user.roles and user.roles[0]
        hidden_types = role and role.hidden_content_types

        return set([
            cls
            for cls in root_type.schema_tree()
            if (
                cls.visible
                and cls.instantiable
                and (not hidden_types or cls not in hidden_types)
                and user.has_permission(CreatePermission, target = cls)
            )
        ])

    def get_dropdown_panel(self, action_bar):

        if action_bar.relation:
            root_type = action_bar.relation.related_type
        else:
            root_type = action_bar.action_target

        instantiable_types = self.get_instantiable_types(root_type)

        if len(instantiable_types) > 1:
            dropdown = templates.new(
                "woost.views.BackOfficeNewItemTypeSelector"
            )
            dropdown.action = self
            dropdown.action_target = action_bar.action_target
            dropdown.selection_field = action_bar.selection_field
            dropdown.relation = action_bar.relation
            dropdown.instantiable_types = instantiable_types
            return dropdown

        return None


class NewAction(CreateAction):
    included = frozenset(["toolbar"])
    excluded = (CreateAction.excluded | frozenset([
        "collection",
        "changelog"
    ])) - frozenset(["selector"])

    def invoke(self, controller, selection, type):
        redirect(controller.edit_uri(type))


class InstallationSyncAction(UserAction):
    included = frozenset(["toolbar", "item_buttons"])
    content_type = SiteInstallation
    min = 1
    max = 1
    show_as_primary_action = "on_content_type"

    def is_permitted(self, user, target):
        return user.has_permission(InstallationSyncPermission)


class SelectRelatedObjectAction(UserAction):
    excluded = frozenset(["integral"])
    ignores_selection = True
    min = None
    max = None
    show_as_primary_action = "always"

    def get_parameter_members(self, controller, selection):
        return [
            schema.MemberReference(
                "relation",
                schemas = [self.content_type or Item],
                enumeration = [
                    member
                    for member in
                        controller.stack_node.item.__class__.iter_members()
                    if isinstance(member, schema.RelationMember)
                ],
                required = True
            )
        ]

    def invoke(self, controller, selection, relation):

        # Add a relation node to the edit stack, and redirect the user
        # there
        node = RelationNode()
        node.member = relation
        node.action = "add"
        controller.edit_stack.push(node)
        controller.edit_stack.go()


class AddAction(SelectRelatedObjectAction):
    included = frozenset([("collection")])


class PickAction(SelectRelatedObjectAction):
    included = frozenset(["reference"])


class RelateNewIntegralObjectAction(CreateAction):

    def get_parameter_members(self, controller, selection):
        return [
            schema.MemberReference(
                "relation",
                schemas = [self.content_type or Item],
                enumeration = [
                    member
                    for member in
                        controller.stack_node.item.__class__.iter_members()
                    if isinstance(member, schema.RelationMember)
                ],
                required = True
            ),
            schema.Reference(
                "type",
                class_family = Item
            ),
            schema.String("text")
        ]

    def invoke(self, controller, selection, relation, type, text = None):
        node = RelationNode()
        node.member = relation
        node.action = "add"
        controller.edit_stack.push(node)

        if text and type.descriptive_member:
            text = unquote(text.encode("utf-8")).decode("utf-8")
            key = "edited_item_%s" % type.descriptive_member.name
            if type.descriptive_member.translated:
                key += "-" + get_language()
            params = {key: text}
        else:
            params = {}

        raise redirect(controller.edit_uri(type, **params))


class AddNewAction(RelateNewIntegralObjectAction):
    included = frozenset([("collection", "integral")])


class PickNewAction(RelateNewIntegralObjectAction):
    included = frozenset([("reference")])


class UnlinkAction(UserAction):
    included = frozenset(["item_selector"])
    excluded = frozenset(["integral"])
    max = 1
    min = 1
    show_as_primary_action = "always"

    def get_parameter_members(self, controller, selection):
        return [
            schema.MemberReference(
                "relation",
                schemas = [self.content_type or Item],
                enumeration = [
                    member
                    for member in
                    controller.stack_node.item.__class__.iter_members()
                    if isinstance(member, schema.RelationMember)
                    ],
                required = True
            )
        ]

    def invoke(self, controller, selection, relation):
        controller.stack_node.form_data[relation.name] = None


class RemoveAction(UserAction):
    included = frozenset([("toolbar", "collection")])
    excluded = frozenset(["integral"])
    max = None
    show_as_primary_action = "always"

    def get_parameter_members(self, controller, selection):
        return [
            schema.MemberReference(
                "relation",
                schemas = [self.content_type or Item],
                enumeration = [
                    member
                    for member in
                        controller.stack_node.item.__class__.iter_members()
                    if isinstance(member, schema.RelationMember)
                ],
                required = True
            )
        ]

    def invoke(self, controller, selection, relation):

        stack_node = controller.stack_node

        for item in selection:
            stack_node.unrelate(relation, item)


class EditAction(UserAction):
    included = frozenset([
        "toolbar",
        "item_buttons",
        "item_selector",
        "block_menu",
        "edit_blocks_toolbar"
    ])
    show_as_primary_action = "always"

    def is_available(self, context, target):

        # Prevent action nesting
        edit_stacks_manager = \
            controller_context.get("edit_stacks_manager")

        if edit_stacks_manager:
            edit_stack = edit_stacks_manager.current_edit_stack
            if edit_stack:
                for node in edit_stack[:-1]:
                    if isinstance(node, EditNode) \
                    and node.item is target:
                        return False

        return UserAction.is_available(self, context, target)

    def get_url(self, controller, selection):
        return controller.edit_uri(selection[0])


class DuplicateAction(UserAction):

    included = frozenset([
        "toolbar",
        "item_buttons"
    ])
    excluded = UserAction.excluded | frozenset([
        "new_item"
    ])
    min = 1
    max = 1
    show_as_primary_action = "always"

    def is_permitted(self, user, target):
        if isinstance(target, type):
            return any(
                model.instantiable
                and user.has_permission(CreatePermission, target = model)
                for model in target.schema_tree()
            )
        else:
            return (
                target.__class__.instantiable
                and user.has_permission(
                    CreatePermission,
                    target = target.__class__
                )
            )

    def invoke(self, controller, selection):

        @transactional()
        def duplicate():
            copy = selection[0].create_copy()
            copy.insert()
            return copy

        copy = duplicate()

        # Update the parent edit session to include the duplicate
        stack = controller.edit_stack
        if stack:
            source_id = selection[0].id
            relations = [
                (
                    member,
                    (copy.get(member).id,)
                    if isinstance(member, schema.Reference)
                    else [item.id for item in copy.get(member)]
                )
                for member in copy.__class__.iter_members()
                if isinstance(member, schema.RelationMember)
                and member.related_end
                and copy.get(member)
            ]
            for node in stack:
                if isinstance(node, EditNode):
                    for relation, rel_ids in relations:
                        if (
                            isinstance(node.item, relation.related_type)
                            and node.item_id in rel_ids
                        ):
                            node.relate(relation.related_end, copy)

        Notification(
            translations(
                "woost.duplicate_created_notice",
                source = selection[0]
            ),
            "success"
        ).emit()
        raise redirect(controller.edit_uri(copy))


class DeleteAction(UserAction):
    included = frozenset([
        ("content_view", "toolbar"),
        ("collection", "toolbar", "integral"),
        ("item_selector", "integral"),
        "item_buttons",
        "block_menu"
    ])
    excluded = frozenset([
        "selector",
        "new_item",
        "calendar_content_view",
        "changelog",
        "common_block"
    ])
    max = None
    show_as_primary_action = "always"

    def is_permitted(self, user, target):
        return user.has_permission(DeletePermission, target = target)


class PreviewAction(UserAction):
    included = frozenset([
        ("item_buttons", "edit")
    ])
    content_type = (Publishable, Block)
    show_as_primary_action = "always"


class OpenResourceAction(UserAction):
    min = 1
    max = 1
    content_type = (Publishable, SiteInstallation, Block)
    included = frozenset([
        "toolbar",
        "item_buttons",
        "edit_blocks_toolbar"
    ])
    excluded = frozenset([
        "new",
        "selector",
        "calendar_content_view",
        "changelog"
    ])
    link_target = "_blank"
    show_as_primary_action = "on_content_type"

    def get_url(self, controller, selection):
        target = selection[0]

        if isinstance(target, Publishable):
            return target.get_uri(host = "?")
        elif isinstance(target, Block):
            for path in target.find_paths():
                container = path[0][0]
                if isinstance(container, Publishable):
                    return container.get_uri(host = "?")
            else:
                return "/"
        else:
            return target.url


class ReferencesAction(UserAction):
    included = frozenset([
        "toolbar",
        "item_buttons"
    ])
    excluded = UserAction.excluded | frozenset([
        "new_item",
        "collection"
    ])
    min = 1
    max = 1

    def is_primary(self, target, context):
        return "item_buttons" in context

    def get_references(self, target):
        references = list(self._iter_references(target))
        references.sort(
            key = lambda ref:
                (translations(ref[0]), translations(ref[1]))
        )
        return references

    def _iter_references(self, obj):
        for member in obj.__class__.iter_members():
            if (
                isinstance(member, schema.RelationMember)
                and member.related_end
                and member.related_end.visible_in_reference_list
                and issubclass(member.related_type, Item)
                and member.related_type.visible
                and not member.integral
            ):
                value = obj.get(member)
                if value:
                    if isinstance(member, schema.Reference):
                        if self._should_include_reference(value, member.related_end):
                            yield value, member.related_end
                    elif isinstance(member, schema.Collection):
                        for item in value:
                            if self._should_include_reference(item, member.related_end):
                                yield item, member.related_end

    def _should_include_reference(self, referrer, relation):
        user = app.user
        return (
            relation.visible
            and user.has_permission(ReadPermission, target = referrer)
            and user.has_permission(ReadMemberPermission, member = relation)
        )


class ShowChangelogAction(UserAction):
    min = None
    max = 1
    excluded = frozenset([
        "selector",
        "new_item",
        "calendar_content_view",
        "changelog",
        "collection"
    ])

    def get_url(self, controller, selection):

        params = self.get_url_params(controller, selection)

        # Filter by target element
        if selection:
            params["filter"] = "changeset-change"
            params["filter_target0"] = str(selection[0].id)

        # Filter by target type
        else:
            user_collection = getattr(controller, "user_collection", None)
            if user_collection and user_collection.type is not Item:
                params["filter"] = "changeset-change"
                params["filter_target_type0"] = user_collection.type.full_name

        return controller.contextual_uri(
            "changelog",
            **params
        )

    def is_permitted(self, user, target):
        return user.has_permission(ReadHistoryPermission)


class ExportAction(UserAction):
    included = frozenset(["toolbar"])
    excluded = UserAction.excluded | frozenset(["collection", "empty_set"])
    min = 1
    max = None
    ignores_selection = True
    format = None
    direct_link = True

    def __init__(self, id, format):
        UserAction.__init__(self, id)
        self.format = format

    def get_url(self, controller, selection):
        return "?" + view_state(
            format = self.format
        )


class InvalidateCacheAction(UserAction):
    min = None
    max = None
    excluded = UserAction.excluded | frozenset(["collection"])

    def is_available(self, context, target):
        return (
            app.cache.enabled
            and app.cache.storage
            and UserAction.is_available(self, context, target)
        )

    def invoke(self, controller, selection):

        if selection is None:
            app.cache.clear()
        else:
            for item in selection:
                item.clear_cache()

        Notification(
            translations("woost.cache_invalidated_notice", subset = selection),
            "success"
        ).emit()


class SelectAction(UserAction):
    included = frozenset([("list_buttons", "selector")])
    excluded = frozenset()
    min = None
    max = None

    def invoke(self, controller, selection):

        stack = controller.edit_stack

        if stack:

            node = stack[-1]
            params = {}

            if isinstance(node, SelectionNode):
                params[node.selection_parameter] = (
                    selection[0].id
                    if selection
                    else ""
                )

            elif isinstance(node, RelationNode):
                edit_state = node.parent_node
                member = controller.stack_node.member

                if isinstance(member, schema.Reference):
                    edit_state.relate(
                        member,
                        None if not selection else selection[0]
                    )
                else:
                    if controller.stack_node.action == "add":
                        modify_relation = edit_state.relate
                    else:
                        modify_relation = edit_state.unrelate

                    for item in selection:
                        modify_relation(member, item)

            stack.go_back(**params)


class GoBackAction(UserAction):
    ignores_selection = True
    min = None
    max = None

    def invoke(self, controller, selection):
        controller.go_back()


class CloseAction(GoBackAction):
    included = frozenset([
        ("item_buttons", "edit"),
        "edit_blocks_toolbar"
    ])
    show_as_primary_action = "always"


class CancelAction(GoBackAction):
    included = frozenset([
        ("list_buttons", "selector")
    ])
    excluded = frozenset()
    show_as_primary_action = "always"


class SaveAction(UserAction):
    included = frozenset([
        ("item_buttons", "new"),
        ("item_buttons", "edit"),
        ("item_buttons", "preview")
    ])
    ignores_selection = True
    max = None
    min = None
    close = False
    show_as_primary_action = "always"

    def is_permitted(self, user, target):
        if target.is_inserted:
            return user.has_permission(
                ModifyPermission,
                target = target
            )
        else:
            return user.has_permission(
                CreatePermission,
                target = target.__class__
            )

    def get_errors(
        self,
        controller,
        selection,
        parameters_schema,
        **parameters
    ):
        for error in UserAction.get_errors(
            self,
            controller,
            selection,
            parameters_schema,
            **parameters
        ):
            yield error

        for error in controller.stack_node.iter_errors():
            yield error

    def invoke(self, controller, selection):
        controller.save_item(close = self.close)


def focus_block(block):
    url_builder = get_request_url_builder()
    url_builder.fragment = "block" + str(block.id)
    url_builder.query.pop("action", None)
    url_builder.query.pop("block_parent", None)
    url_builder.query.pop("block_slot", None)
    url_builder.query.pop("block", None)
    raise redirect(url_builder)


class EditBlocksAction(UserAction):
    min = 1
    max = 1
    included = frozenset(["toolbar", "item_buttons"])
    excluded = UserAction.excluded | frozenset(["new_item"])
    show_as_primary_action = "on_content_type"

    def is_primary(self, target, context):
        return (
            target in (Publishable, Document)
            or UserAction.is_primary(self, target, context)
        )

    def matches_content_type(self, target, accept_ancestors = True):
        if isinstance(target, type):
            content_type = target
        else:
            content_type = target.__class__

        if accept_ancestors:
            return schema_tree_has_block_container(content_type)
        else:
            return type_is_block_container(content_type)

    def is_available(self, context, target):

        if not UserAction.is_available(self, context, target):
            return False

        if not isinstance(target, type):

            # Prevent action nesting
            edit_stacks_manager = \
                controller_context.get("edit_stacks_manager")

            if edit_stacks_manager:
                edit_stack = edit_stacks_manager.current_edit_stack
                if edit_stack:
                    for node in edit_stack:
                        if isinstance(node, EditBlocksNode) \
                        and node.item is target:
                            return False

        return True

    def is_permitted(self, user, target):
        return user.has_permission(ModifyPermission, target = target)

    def get_url(self, controller, selection):

        params = {}
        edit_stack = controller.edit_stack

        if edit_stack:
            params["edit_stack"] = edit_stack.to_param()

        return controller.contextual_uri("blocks", selection[0].id, **params)


class AddBlockAction(UserAction):
    min = None
    max = None
    ignore_selection = True
    included = frozenset(["blocks_slot_toolbar"])
    block_positioning = "append"
    show_as_primary_action = "always"

    @request_property
    def block_type(self):
        return get_parameter(
            schema.Reference("block_type", class_family = Block)
        )

    @request_property
    def common_block(self):
        return get_parameter(schema.Reference("common_block", type = Block))

    def invoke(self, controller, selection):

        common_block = self.common_block

        # Add a reference to a common block
        if common_block:
            add_block(
                common_block,
                controller.block_parent,
                controller.block_slot,
                positioning = self.block_positioning,
                anchor = controller.block
            )
            datastore.commit()
            focus_block(common_block)

        # Add a new block: set up an edit stack node and redirect the user
        else:
            edit_stacks_manager = controller.context["edit_stacks_manager"]
            edit_stack = edit_stacks_manager.current_edit_stack

            block = self.block_type()
            node_class = resolve(block.edit_node_class)
            node = node_class(
                block,
                visible_translations = controller.visible_languages
            )
            node.block_parent = controller.block_parent
            node.block_slot = controller.block_slot
            node.block_positioning = self.block_positioning
            node.block_anchor = controller.block
            edit_stack.push(node)

            edit_stacks_manager.preserve_edit_stack(edit_stack)
            edit_stack.go()


class AddBlockBeforeAction(AddBlockAction):
    included = frozenset(["block_menu"])
    block_positioning = "before"
    show_as_primary_action = "always"


class AddBlockAfterAction(AddBlockAction):
    included = frozenset(["block_menu"])
    block_positioning = "after"
    show_as_primary_action = "always"


class RemoveBlockAction(UserAction):
    content_type = Block
    included = frozenset(["block_menu"])
    show_as_primary_action = "always"

    def is_available(self, context, target):
        return (
            UserAction.is_available(self, context, target)
            and target.is_common_block()
        )

    def invoke(self, controller, selection):

        collection = controller.block_parent.get(controller.block_slot)

        try:
            index = collection.index(selection[0])
        except ValueError:
            index = None

        schema.remove(collection, selection[0])
        datastore.commit()

        # Focus the block that was nearest to the removed block
        if index is None or not collection:
            adjacent_block = controller.block_parent
        elif index > 0:
            adjacent_block = collection[index - 1]
        else:
            adjacent_block = collection[0]

        focus_block(adjacent_block)


BLOCK_CLIPBOARD_SESSION_KEY = "woost.block_clipboard"

def get_block_clipboard_contents():
    return session.get(BLOCK_CLIPBOARD_SESSION_KEY)

def set_block_clipboard_contents(contents):
    session[BLOCK_CLIPBOARD_SESSION_KEY] = contents


class CopyBlockAction(UserAction):
    content_type = Block
    included = frozenset(["block_menu"])
    show_as_primary_action = "always"

    def invoke(self, controller, selection):
        set_block_clipboard_contents({
            "mode": "copy",
            "block": controller.block.id,
            "block_parent": controller.block_parent.id,
            "block_slot": controller.block_slot.name
        })
        focus_block(controller.block)


class CutBlockAction(UserAction):
    content_type = Block
    included = frozenset(["block_menu"])
    show_as_primary_action = "always"

    def invoke(self, controller, selection):
        set_block_clipboard_contents({
            "mode": "cut",
            "block": controller.block.id,
            "block_parent": controller.block_parent.id,
            "block_slot": controller.block_slot.name
        })
        focus_block(controller.block)


class PasteBlockAction(UserAction):
    included = frozenset(["blocks_slot_toolbar"])
    block_positioning = "append"
    show_as_primary_action = "always"

    def is_available(self, context, target):

        if UserAction.is_available(self, context, target):
            clipboard = get_block_clipboard_contents()
            if clipboard:
                allows_block_type = getattr(target, "allows_block_type", None)
                if (
                    allows_block_type is None
                    or allows_block_type(
                        Block.require_instance(clipboard["block"]).__class__
                    )
                ):
                    return True

        return False

    def invoke(self, controller, selection):
        clipboard = get_block_clipboard_contents()

        if not clipboard:
            Notification(
                translations("woost.block_clipboard.empty"),
                "error"
            ).emit()
        else:
            try:
                block = Block.require_instance(clipboard["block"])
                src_parent = Item.require_instance(clipboard["block_parent"])
                src_slot = type(src_parent).get_member(clipboard["block_slot"])
            except:
                Notification(
                    translations("woost.block_clipboard.error"),
                    "error"
                ).emit()
            else:
                # Remove the block from the source location
                if clipboard["mode"] == "cut":
                    if isinstance(src_slot, schema.Reference):
                        src_parent.set(src_slot, None)
                    elif isinstance(src_slot, schema.Collection):
                        src_collection = src_parent.get(src_slot)
                        schema.remove(src_collection, block)
                # Or copy it
                elif clipboard["mode"] == "copy":
                    block = block.create_copy()
                    block.insert()

                # Add the block to its new position
                add_block(
                    block,
                    controller.block_parent,
                    controller.block_slot,
                    positioning = self.block_positioning,
                    anchor = controller.block
                )

                datastore.commit()
                del session[BLOCK_CLIPBOARD_SESSION_KEY]
                focus_block(block)


class PasteBlockBeforeAction(PasteBlockAction):
    included = frozenset(["block_menu"])
    block_positioning = "before"


class PasteBlockAfterAction(PasteBlockAction):
    included = frozenset(["block_menu"])
    block_positioning = "after"


class ShareBlockAction(UserAction):
    content_type = Block
    included = frozenset(["block_menu"])
    show_as_primary_action = "always"

    def is_available(self, context, target):
        return (
            UserAction.is_available(self, context, target)
            and not target.is_common_block()
        )

    def is_permitted(self, user, target):
        config = Configuration.instance
        return (
            UserAction.is_permitted(self, user, target)
            and user.has_permission(ModifyPermission, target = config)
            and user.has_permission(ModifyPermission, target = target)
            and user.has_permission(
                ModifyMemberPermission,
                member = Configuration.common_blocks
            )
        )

    def invoke(self, controller, selection):
        Configuration.instance.common_blocks.append(selection[0])
        datastore.commit()
        focus_block(selection[0])

# Action registration
#------------------------------------------------------------------------------
NewAction("new").register()
AddAction("add").register()
AddNewAction("add_new").register()
PickAction("pick").register()
PickNewAction("pick_new").register()
UnlinkAction("unlink").register()
RemoveAction("remove").register()
AddBlockAction("add_block").register()
AddBlockBeforeAction("add_block_before").register()
AddBlockAfterAction("add_block_after").register()
EditAction("edit").register()
EditBlocksAction("edit_blocks").register()
DuplicateAction("duplicate").register()
InstallationSyncAction("installation_sync").register()
CopyBlockAction("copy_block").register()
CutBlockAction("cut_block").register()
PasteBlockAction("paste_block").register()
PasteBlockBeforeAction("paste_block_before").register()
PasteBlockAfterAction("paste_block_after").register()
ShareBlockAction("share_block").register()
RemoveBlockAction("remove_block").register()
DeleteAction("delete").register()
ExportAction("export_xls", "msexcel").register()
InvalidateCacheAction("invalidate_cache").register()
ReferencesAction("references").register()
ShowChangelogAction("changelog").register()
OpenResourceAction("open_resource").register()
save_and_close = SaveAction("save_and_close")
save_and_close.close = True
save_and_close.register()
CloseAction("close").register()
CancelAction("cancel").register()
SaveAction("save").register()
PreviewAction("preview").register()
SelectAction("select").register()

# Translation
#------------------------------------------------------------------------------
translations.load_bundle("woost.controllers.backoffice.useractions")

@translations.instances_of(UserAction)
def translate_user_action(user_action, **kwargs):
    return translations("woost.actions." + user_action.id, **kwargs)

