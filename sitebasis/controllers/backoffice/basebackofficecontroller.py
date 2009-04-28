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
    RelationNode,
    WrongEditStackError,
    EditStackExpiredError
)


class BaseBackOfficeController(BaseCMSController):

    section = None
    persistent_content_type_choice = False
    settings_duration = 60 * 60 * 24 * 30 # ~= 1 month

    def get_edit_uri(self, target, *args, **kwargs):
        
        params = kwargs or {}
        edit_stack = self.edit_stack

        if edit_stack and "edit_stack" not in params:
            params["edit_stack"] = edit_stack.to_param()

        # URI for new items
        if isinstance(target, type) or not target.is_inserted:
            target_id = "new"
            
            # TODO: Use full names to identify types
            if not edit_stack:
                params["type"] = target.name

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

    @getter
    def edit_stack(self):
        return self.context["edit_stacks_manager"].current_edit_stack

    @getter
    def stack_node(self):
        stack = self.edit_stack
        return stack and stack[-1]

    @getter
    def edit_node(self):
        stack = self.edit_stack
        if stack:
            return stack[-1].get_ancestor_node(EditNode)
        return None

    @getter
    def relation_node(self):
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

    def notify_user(self, message, category = None):
        notifications = cherrypy.session.get("notifications")
        if notifications is None:
            cherrypy.session["notifications"] = notifications = []
        notifications.append((message, category))

    def pop_user_notifications(self):
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

