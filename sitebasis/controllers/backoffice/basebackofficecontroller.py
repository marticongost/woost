#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from __future__ import with_statement
from itertools import chain
from urllib import urlencode
import cherrypy
from cocktail.modeling import getter, cached_getter
from cocktail.iteration import first
from cocktail.translations import translations
from cocktail.events import event_handler
from cocktail.schema import String
from cocktail.language import get_content_language
from cocktail.controllers import get_persistent_param
from sitebasis.models import Item
from sitebasis.controllers import BaseCMSController
from sitebasis.controllers.backoffice.useractions import get_user_action
from sitebasis.controllers.backoffice.editstack import (
    EditNode,
    SelectionNode,
    RelationNode,
    WrongEditStackError,
    EditStackExpiredError
)


class BaseBackOfficeController(BaseCMSController):
    """Base class for all backoffice controllers."""

    section = None
    settings_duration = 60 * 60 * 24 * 30 # ~= 1 month

    def get_edit_uri(self, target, *args, **kwargs):
        """Get the URI of the edit page of the specified item.
        
        @param target: The item or content type to get the URI for.
        @type target: L{Item<sitebasis.models.Item>} instance or class

        @param args: Additional path components that will be appended to the
            produced URI.
        @type args: unicode

        @param kwargs: Additional query string parameters that will be added
            to the produced URI.

        @return: The produced URI.
        @rtype: unicode
        """        
        params = kwargs or {}
        edit_stack = self.edit_stack

        if edit_stack and "edit_stack" not in params:
            params["edit_stack"] = edit_stack.to_param()

        # URI for new items
        if isinstance(target, type) or not target.is_inserted:
            target_id = "new"
            if edit_stack is None \
            or ("edit_stack" in params and params["edit_stack"] is None):
                params["type"] = target.full_name

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
            uri += "?" + urlencode(
                dict((k, v) for k, v in params.iteritems() if v is not None),
                True
            )

        return uri

    @cached_getter
    def persistence_prefix(self):
        stack = self.edit_stack
        return stack.to_param() if stack else ""

    @cached_getter
    def content_type_persistence_prefix(self):
        full_prefix = self.content_type.full_name
        prefix = self.persistence_prefix
        if prefix:
            full_prefix += "-" + prefix
        return full_prefix        

    @cached_getter
    def persistence_duration(self):
        node = self.stack_node
        return (
            None
            if node and isinstance(node, (RelationNode, SelectionNode))
            else self.settings_duration
        )

    def get_content_type(self, default = None):
        """Gets the content type that is selected by the current HTTP request.
        
        @param default: If specified, this value will be used as the return
            value if no content type is explicitly specified by the request.
        @type default: L{Item<sitebasis.models.Item>} class

        @return: The selected content type.
        @rtype: L{Item<sitebasis.models.Item>}
        """
        cookie_name = "type"
        prefix = self.persistence_prefix
        if prefix:
            cookie_name = prefix + "-" + cookie_name

        type_param = get_persistent_param(
            "type",
            cookie_name = cookie_name,
            cookie_duration = self.persistence_duration
        )

        if type_param is None:
            return default
        else:
            for content_type in chain([Item], Item.derived_schemas()):
                if content_type.full_name == type_param:
                    return content_type

    def get_visible_languages(self):
        """Obtains the list of languages in which data will be displayed for
        the current HTTP request.
        
        @return: A set containing all the languages enabled by the present
            request. Each language is represented using its two letter ISO
            code.
        @rtype: set of str
        """
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
            return set([get_content_language()])

    @getter
    def edit_stack(self):
        """The edit stack for the current request.
        @type: L{EditStack<sitebasis.controllers.backoffice.editstack.EditStack>}
        """
        return self.context["edit_stacks_manager"].current_edit_stack

    @getter
    def stack_node(self):
        """The top node of the edit stack for the current request.
        @type: L{StackNode<sitebasis.controllers.backoffice.editstack.StackNode>}
        """
        stack = self.edit_stack
        return stack and stack[-1]

    @getter
    def edit_node(self):
        """The topmost edit node of the edit stack for the current request.
        @type: L{EditNode<sitebasis.controllers.backoffice.editstack.EditNode>}
        """
        stack = self.edit_stack
        if stack:
            return stack[-1].get_ancestor_node(EditNode)
        return None

    @getter
    def relation_node(self):
        """The topmost relation node of the edit stack for the current request.
        @type: L{RelationNode<sitebasis.controllers.backoffice.editstack.RelationNode>}
        """
        stack = self.edit_stack
        if stack:
            return stack[-1].get_ancestor_node(RelationNode)
        return None

    @cached_getter
    def output(self):
        output = BaseCMSController.output(self)
        output.update(
            backoffice = self.context["document"],
            section = self.section,
            edit_stack = self.edit_stack,
            notifications = self.pop_user_notifications(),
            get_edit_uri = self.get_edit_uri
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

    def notify_user(self, message, category = None, transient = True):
        """Creates a new notification for the current user.
        
        Notifications are stored until a proper page is served to the user. It
        is up to the views to decide how these messages should be displayed.

        @param message: The message that will be shown to the user.
        @type message: unicode

        @param category: An optional free form string identifier that qualifies
            the message. Standard values include 'success' and 'error'.
        @type category: unicode

        @param transient: Indicates if the message should be hidden after a
            short lapse (True), or if it should remain visible until explicitly
            closed by the user (False).
        @type transient: bool
        """
        notifications = cherrypy.session.get("notifications")
        if notifications is None:
            cherrypy.session["notifications"] = notifications = []
        notifications.append((message, category, transient))

    def pop_user_notifications(self):
        """Retrieves pending notification messages that were stored through the
        L{notify_user} method.

        Retrieved messages are considered to be consumed, and therefore they
        are removed from the list of pending notifications.

        @return: The sequence of pending notification messages. Each message
            consists of a tuple with the message text, its category and wether
            or not it should be treated as a transient message.
        @rtype: sequence of (tuple of (unicode, unicode or None, bool))
        """
        notifications = cherrypy.session.get("notifications")
        cherrypy.session["notifications"] = []
        return notifications

    @event_handler
    def handle_exception_raised(cls, event):

        # Redirect the user to the backoffice root when failing to load an edit
        # stack node
        if isinstance(
            event.exception,
            (EditStackExpiredError, WrongEditStackError)
        ):
            event.source.notify_user(translations(event.exception), "error")
            raise cherrypy.HTTPRedirect(event.source.document_uri())


class EditStateLostError(Exception):
    """An exception raised when a user requests an edit state that is no longer
    available."""

