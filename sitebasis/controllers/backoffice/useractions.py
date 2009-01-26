#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
import cherrypy
from cocktail.modeling import getter, ListWrapper
from cocktail.pkgutils import get_full_name
from sitebasis.models import Document


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

def get_view_actions(view, container, content_type):
    """Obtains the list of actions that can be displayed on a given view.

    @param view: The view where the action will be displayed.
    @type view: L{Element<cocktail.html.element.Element>}
    
    @param container: A user interface container where the action will be
        inserted. This should be a string identifier, such as "context_menu",
        "toolbar", etc. Different views can make use of as many different
        identifiers as they require.
    @type container: str

    @param content_type: The content type affected by the action.
    @type content_type: L{Item<sitebasis.models.item.Item>} class

    @return: The list of user actions available under the specified context.
    @rtype: iterable L{UserAction} sequence
    """
    return (action
            for action in _action_list
            if action.is_available(view, container, content_type))

class UserAction(object):
    """An action that is made available to users at the backoffice
    interface. The user actions model allows site implementors to extend the
    site with their own actions, or to disable or override standard actions
    with fine grained control of their context.

    @ivar enabled: Controls the site-wide availavility of the action.
    @type enabled: bool

    @ivar frequent: Indicates if the action is frequently accessed by users,
        and should therefore be promoted to a more visible space on the user
        interface.
    @type frequent: bool

    @ivar min: The minimum number of content items that the action can be
        invoked on. Setting it to 0 or None disables the constraint.
    @type min: int

    @ivar max: The maximum number of content items that the action can be
        invoked on. A value of None disables the constraint.
    @type max: int
    """

    enabled = True
    frequent = False
    authorization_context = None
    ignores_selection = False
    min = 1
    max = 1

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

    def is_available(self, view, container, content_type):
        """Indicates if the user action is available under a certain context.

        By default, actions are available under any context. Subclasses that
        want to change this behavior should override this method as required.
        
        @param view: The view where the action will be inserted.
        @type view: L{Element<cocktail.html.element.Element>}
        
        @param container: A user interface container where the action will be
            inserted. This should be a string identifier, such as
            "context_menu", "toolbar", etc. Different views can make use of as
            many different identifiers as they require.
        @type container: str

        @param content_type: The content type affected by the action.
        @type content_type: L{Item<sitebasis.models.item.Item>} class

        @return: True if the action can be shown in the given context, False
            otherwise.
        @rtype: bool
        """
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
        if self.min == self.max == 1:
            # Single selection
            return controller.get_edit_uri(
                    selection[0],
                    self.id)     
        else:
            return controller.document_uri(
                    self.id,
                    selection = [item.id for item in selection])


class SelectionError(Exception):
    """An exception produced by the L{UserAction.get_errors} method when an
    action is attempted against an invalid number of items."""
    
    def __init__(self, action, selection_size):
        Exception.__init__("Can't execute action '%s' on %d item(s)."
            % (action.id, selection_size))
        self.action = action
        self.selection_size = selection_size


# Implementation of concrete actions
#------------------------------------------------------------------------------

def _match_view(view, *args):    
 
    names = []

    for arg in args:
        pos = arg.rfind(".")
        name = arg[pos + 1:]
        full_name = arg[:pos] + "." + name.lower() + "." + name
        names.append(full_name)

    for cls in view.__class__._classes:
        if get_full_name(cls) in names:
            return True
    
    return False
    
def _match_view_ancestor(view, class_name):

    parent = view.parent

    while parent:
        if _match_view(parent, class_name):
            return True
        parent = parent.parent

    return False


class CreateAction(UserAction):
    frequent = True
    ignores_selection = True
    min = None
    max = None
    
    def get_url(self, controller, selection):
        return controller.get_edit_uri(controller.edited_content_type)

    def is_available(self, view, container, content_type):
        return (
            _match_view(view, "sitebasis.views.ContentView")
            and not _match_view_ancestor(
                view,
                "sitebasis.views.BackOfficeCollectionView")
        )


#class CreateBeforeAction(CreateAction):
#   ignores_selection = False


#class CreateInsideAction(CreateAction):
#   ignores_selection = False


#class CreateAfterAction(CreateAction):
#   ignores_selection = False


class MoveAction(UserAction):
    frequent = True
    max = None

    def is_available(self, view, container, content_type):
        return _match_view(view, "sitebasis.views.TreeContentView")


class AddAction(UserAction):
    frequent = True
    ignores_selection = True

    # TODO: def invoke()

    def is_available(self, view, container, content_type):        
        return (
            _match_view(view, "sitebasis.views.ContentView")
            and _match_view_ancestor(view,
                "sitebasis.views.BackOfficeCollectionView")
        )


class RemoveAction(UserAction):
    frequent = True
    max = None

    # TODO: def invoke()

    def is_available(self, view, container, content_type):
        return (
            _match_view(view, "sitebasis.views.ContentView")
            and _match_view_ancestor(view,
                "sitebasis.views.BackOfficeCollectionView")
        )


class OrderAction(UserAction):
    frequent = True
    max = None

    def is_available(self, view, container, content_type):
        return _match_view(view, "sitebasis.views.OrderContentView")


class ViewDetailAction(UserAction):
    frequent = True
    
    def is_available(self, view, container, content_type):
        return not _match_view(view, "sitebasis.views.BackOfficeDetailView")


class EditAction(UserAction):
    frequent = True

    def get_url(self, controller, selection):
        return controller.get_edit_uri(selection[0])

    def is_available(self, view, container, content_type):
        return not _match_view(
            view,
            "sitebasis.views.BackOfficeEditView",
            "sitebasis.views.BackOfficeCollectionView"
        )


class DeleteAction(UserAction):
    frequent = True
    max = None

    def is_available(self, view, container, content_type):
        return not _match_view_ancestor(
            view,
            "sitebasis.views.BackOfficeCollectionView"
        )


class HistoryAction(UserAction):
    min = None


class DiffAction(UserAction):
    
    def is_available(self, view, container, content_type):
        return not _match_view(view, "sitebasis.views.BackOfficeDiffView")


class PreviewAction(UserAction):

    def is_available(self, view, container, content_type):
        return (
            issubclass(content_type, Document)
            and not _match_view(view, "sitebasis.views.BackOfficePreview")
        )


class ExportAction(UserAction):
    max = None

    def is_available(self, view, container, content_type):
        return _match_view(view, "sitebasis.views.ContentView")


CreateAction("new").register()
MoveAction("move").register()
AddAction("add").register()
RemoveAction("remove").register()
OrderAction("order").register()
ViewDetailAction("view").register()
EditAction("edit").register()
DeleteAction("delete").register()
DiffAction("diff").register()
HistoryAction("history").register()
PreviewAction("preview").register()
ExportAction("export_xls").register()
ExportAction("export_csv").register()

