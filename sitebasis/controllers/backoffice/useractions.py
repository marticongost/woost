#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
import cherrypy
from cocktail.modeling import getter, ListWrapper
from cocktail.pkgutils import get_full_name
from cocktail import schema
from sitebasis.models import Document
from sitebasis.controllers.backoffice.editstack import EditNode, RelationNode


# User action model declaration
#------------------------------------------------------------------------------

# Class stub (needed by the metaclass)
UserAction = None

_action_list = ListWrapper([])
_action_map = {}

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

def get_view_actions(context, content_type):
    """Obtains the list of actions that can be displayed on a given view.

    @param context: A set of string identifiers, such as "context_menu",
        "toolbar", etc. Different views can make use of as many different
        identifiers as they require.
    @type container: str set

    @param content_type: The content type affected by the action.
    @type content_type: L{Item<sitebasis.models.item.Item>} class

    @return: The list of user actions available under the specified context.
    @rtype: iterable L{UserAction} sequence
    """
    return (
        action
        for action in _action_list
        if action.enabled
            and action.is_available(context, content_type)
    )

def add_view_action_context(view, clue):
    """Adds contextual information to the given view, to be gathered by
    L{get_view_actions_context} and passed to L{get_view_actions}.
    
    @param view: The view that gains the context clue.
    @type view: L{Element<cocktail.html.element.Element>}

    @param clue: The context identifier added to the view.
    @type clue: str
    """
    view_context = getattr(view, "actions_context", None)
    if view_context is None:
        view_context = set()
        view.actions_context = view_context
    view_context.add(clue)

def get_view_actions_context(view):
    """Extracts clues on the context that applies to a given view and its
    ancestors, to supply to the L{get_view_actions} function.
    
    @param view: The view to inspect.
    @type view: L{Element<cocktail.html.element.Element>}

    @return: The set of context identifiers for the view and its ancestors.
    @rtype: str set
    """
    context = set()

    while view:
        view_context = getattr(view, "actions_context", None)
        if view_context:
            context.update(view_context)
        view = view.parent
     
    return context


class UserAction(object):
    """An action that is made available to users at the backoffice
    interface. The user actions model allows site implementors to extend the
    site with their own actions, or to disable or override standard actions
    with fine grained control of their context.

    @ivar enabled: Controls the site-wide availavility of the action.
    @type enabled: bool

    @ivar min: The minimum number of content items that the action can be
        invoked on. Setting it to 0 or None disables the constraint.
    @type min: int

    @ivar max: The maximum number of content items that the action can be
        invoked on. A value of None disables the constraint.
    @type max: int
    """
    enabled = True
    included = frozenset(["toolbar_extra", "item_buttons_extra"])
    excluded = frozenset(["selector"])
    authorization_context = None
    ignores_selection = False
    min = 1
    max = 1
    direct_link = False

    def __init__(self, id):

        if not id:
            raise ValueError("User actions must have an id")

        if not isinstance(id, basestring):
            raise TypeError("User action identifiers must be strings, not %s"
                            % type(id))
        self._id = id

    @getter
    def id(self):
        """The unique identifier for the action.
        @type: str
        """
        return self._id

    def register(self):
        """Registers the action with the site, so that it can appear on action
        containers and be handled by controllers.

        Registering an action with an identifier already in use is allowed, and
        will override the previously registered action.
        """
        prev_action = get_user_action(self._id)

        if prev_action:
            pos = _action_list.find(prev_action)
            _action_list._items[pos] = self
        else:
            _action_list._items.append(self)

        _action_map[self._id] = self

    def is_available(self, context, content_type):
        """Indicates if the user action is available under a certain context.

        By default, actions are available under any context. Subclasses that
        want to change this behavior should override this method as required.
        
        @param context: A set of string identifiers, such as "context_menu",
            "toolbar", etc. Different views can make use of as many different
            identifiers as they require.
        @type container: str set

        @param content_type: The content type affected by the action.
        @type content_type: L{Item<sitebasis.models.item.Item>} class

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

    def get_errors(self, controller, selection):
        """Validates the context of an action before it is invoked.

        @param controller: The controller that invokes the action.
        @type controller: L{Controller<cocktail.controllers.controller.Controller>}

        @param selection: The collection of items that the action will be
            applied to.
        @type selection: L{Item<sitebasis.models.item.Item>} collection

        @return: The list of errors for the indicated context.
        @rtype: iterable L{Exception} sequence
        """
        if not self.ignores_selection:

            # Validate selection size
            selection_size = len(selection)

            if (self.min and selection_size < self.min) \
            or (self.max is not None and selection_size > self.max):
                yield SelectionError(self, selection_size)                       

    def invoke(self, controller, selection):
        """Delegates control of the current request to the action. Actions can
        override this method to implement their own response logic; by default,
        users are redirected to an action specific controller.

        @param controller: The controller that invokes the action.
        @type controller: L{Controller<cocktail.controllers.controller.Controller>}
        """
        raise cherrypy.HTTPRedirect(self.get_url(controller, selection))
    
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
        @type selection: L{Item<sitebasis.models.item.Item>} collection

        @return: The URL where the user should be redirected.
        @rtype: str
        """
        params = self.get_url_params(controller, selection)

        if controller.edit_stack:
            params["edit_stack"] = controller.edit_stack.to_param()

        if self.ignores_selection:
            return controller.document_uri(
                self.id,
                **params)

        elif self.min == self.max == 1:
            # Single selection
            return controller.get_edit_uri(
                    selection[0],
                    self.id,
                    **params)
        else:
            return controller.document_uri(
                    self.id,
                    selection = [item.id for item in selection],
                    **params)

    def get_url_params(self, controller, selection):
        """Produces extra URL parameters for the L{get_url} method.
        
        @param controller: The controller that invokes the action.
        @type controller: L{Controller<cocktail.controllers.controller.Controller>}

        @param selection: The collection of items that the action is invoked
            on.
        @type selection: L{Item<sitebasis.models.item.Item>} collection

        @return: A mapping containing additional parameters to include on the
            URL associated to the action.
        @rtype: dict
        """
        return {}


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
    included = frozenset(["toolbar"])
    excluded = frozenset(["collection"])
    ignores_selection = True
    min = None
    max = None
    
    def get_url(self, controller, selection):
        return controller.get_edit_uri(controller.edited_content_type)

#class CreateBeforeAction(CreateAction):
#   ignores_selection = False


#class CreateInsideAction(CreateAction):
#   ignores_selection = False


#class CreateAfterAction(CreateAction):
#   ignores_selection = False


class MoveAction(UserAction):
    included = frozenset([("toolbar", "tree")])
    max = None


class AddAction(UserAction):
    included = frozenset([("toolbar", "collection")])
    excluded = frozenset(["integral"])
    ignores_selection = True
    min = None
    max = None

    def invoke(self, controller, selection):
        
        # Add a relation node to the edit stack, and redirect the user
        # there
        node = RelationNode()
        node.member = controller.member
        node.action = "add"
        controller.edit_stack.push(node)
        controller.edit_stack.go()


class AddIntegralAction(UserAction):

    included = frozenset([("collection", "toolbar", "integral")])
    ignores_selection = True
    min = None
    max = None
    
    def get_url(self, controller, selection):        
        return controller.get_edit_uri(controller.root_content_type)


class RemoveAction(UserAction):
    included = frozenset([("toolbar", "collection")])
    excluded = frozenset(["integral"])
    max = None

    def invoke(self, controller, selection):

        stack_node = controller.stack_node

        for item in selection:
            stack_node.unrelate(controller.member, item)

        controller.user_collection.base_collection = \
            schema.get(stack_node.form_data, controller.member)


class OrderAction(UserAction):
    included = frozenset([("toolbar", "order")])
    max = None

    def invoke(self, controller, selection):
        node = RelationNode()
        node.member = controller.member
        node.action = "order"
        controller.edit_stack.push(node)
        UserAction.invoke(self, controller, selection)

    def get_url_params(self, controller, selection):
        return {"member": self.member.name}


class ShowDetailAction(UserAction):
    included = frozenset(["toolbar", "item_buttons"])


class EditAction(UserAction):
    included = frozenset(["toolbar", "item_buttons"])

    def get_url(self, controller, selection):
        return controller.get_edit_uri(selection[0])


class DeleteAction(UserAction):
    included = frozenset([
        ("content", "toolbar"),
        ("collection", "toolbar", "integral"),
        "item_buttons"
    ])
    excluded = frozenset(["selector", "new_item"])
    max = None


class HistoryAction(UserAction):
    min = None
    excluded = frozenset(["selector", "new_item"])


class DiffAction(UserAction):
    included = frozenset(["item_buttons"])


class RevertAction(UserAction):
    included = frozenset([("diff", "item_body_buttons", "changed")])

    def invoke(self, controller, selection):

        reverted_members = controller.params.read(
            schema.Collection("reverted_members",
                type = set,
                items = schema.String
            )
        )

        stack_node = controller.stack_node

        form_data = stack_node.form_data
        form_schema = stack_node.form_schema
        languages = set(
            list(stack_node.translations)
            + list(stack_node.item.translations.keys())
        )

        source = {}
        stack_node.export_form_data(stack_node.item, source)
        
        for member in form_schema.members().itervalues():
                      
            if member.translated:
                for lang in languages:
                    if (member.name + "-" + lang) in reverted_members:
                        schema.set(
                            form_data,
                            member.name,
                            schema.get(source, member.name, language = lang),
                            language = lang
                        )
            elif member.name in reverted_members:
                schema.set(
                    form_data,
                    member.name,
                    schema.get(source, member.name)
                )


class PreviewAction(UserAction):
    included = frozenset(["toolbar_extra", "item_buttons"])

    def is_available(self, context, content_type):
        return UserAction.is_available(self, context, content_type) \
            and issubclass(content_type, Document)


class ExportAction(UserAction):
    included = frozenset(["toolbar_extra"])
    min = None
    max = None
    ignores_selection = True
    format = None
    direct_link = True

    def __init__(self, id, format):
        UserAction.__init__(self, id)
        self.format = format

    def get_url(self, controller, selection):
        return controller.document_uri(format = self.format)


class SelectAction(UserAction):
    included = frozenset([("list_buttons", "selector")])
    excluded = frozenset()
    min = None
    max = None
    
    def invoke(self, controller, selection):

        edit_state = controller.edit_stack[-2]
        member = controller.stack_node.member

        if isinstance(member, schema.Reference):
            edit_state.relate(member, None if not selection else selection[0])
        else:
            if controller.stack_node.action == "add":
                modify_relation = edit_state.relate 
            else:
                modify_relation = edit_state.unrelate 

            for item in selection:
                modify_relation(member, item)
            
        controller.edit_stack.go(-2)


class GoBackAction(UserAction):
    ignores_selection = True
    min = None
    max = None

    def invoke(self, controller, selection):
        controller.go_back()


class CloseAction(GoBackAction):
    included = frozenset(["item_buttons"])
    excluded = frozenset(["changed", "new", "edit"])


class CancelAction(GoBackAction):
    included = frozenset([
        ("list_buttons", "selector"),
        ("item_buttons", "edit"),
        ("item_buttons", "changed"),
        ("item_buttons", "new")
    ])
    excluded = frozenset()


class SaveAction(UserAction):
    included = frozenset([
        ("item_buttons", "new"),
        ("item_buttons", "edit"),
        ("item_buttons", "changed")
    ])
    ignores_selection = True
    max = None
    min = None
    make_draft = False

    def get_errors(self, controller, selection):
        for error in UserAction.get_errors(self, controller, selection):
            yield error

        for error in controller.stack_node.iter_errors():
            yield error

    def invoke(self, controller, selection):
        controller.save_item(make_draft = self.make_draft)


class SaveDraftAction(SaveAction):
    make_draft = True
    included = frozenset([
        ("item_buttons", "new"),
        ("item_buttons", "edit"),
        ("item_buttons", "changed")
    ])
    excluded = frozenset(["draft"])


class ConfirmDraftAction(UserAction):
    included = frozenset([("item_buttons", "draft")])
    
    def invoke(self, controller, selection):
        raise ValueError("Not implemented")


class DiscardDraftAction(UserAction):
    included = frozenset([("item_buttons", "draft")])

    def invoke(self, controller, selection):
        raise ValueError("Not implemented")


CreateAction("new").register()
MoveAction("move").register()
AddAction("add").register()
AddIntegralAction("add_integral").register()
RemoveAction("remove").register()
OrderAction("order").register()
ShowDetailAction("show_detail").register()
PreviewAction("preview").register()
EditAction("edit").register()
DiffAction("diff").register()
RevertAction("revert").register()
HistoryAction("history").register()
DeleteAction("delete").register()
ExportAction("export_xls", "msexcel").register()
CloseAction("close").register()
CancelAction("cancel").register()
SaveAction("save").register()
SaveDraftAction("save_draft").register()
ConfirmDraftAction("confirm_draft").register()
SelectAction("select").register()
