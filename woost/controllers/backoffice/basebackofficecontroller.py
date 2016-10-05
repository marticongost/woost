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
from cocktail.modeling import getter, cached_getter, OrderedSet
from cocktail.iteration import first
from cocktail.stringutils import normalize
from cocktail.translations import translations, get_language
from cocktail.events import event_handler
from cocktail import schema
from cocktail.controllers import (
    get_parameter,
    request_property,
    redirect,
    CookieParameterSource
)
from woost import app
from woost.models import (
    Configuration,
    Item,
    UserView,
    ReadTranslationPermission
)
from woost.controllers import BaseCMSController
from woost.controllers.notifications import Notification
from woost.controllers.backoffice.useractions import (
    get_user_action,
    SelectionError
)
from woost.controllers.backoffice.editstack import (
    EditNode,
    SelectionNode,
    RelationNode,
    WrongEditStackError
)

translations.load_bundle("woost.controllers.backoffice.basebackofficecontroller")


class BaseBackOfficeController(BaseCMSController):
    """Base class for all backoffice controllers."""

    section = None
    settings_duration = 60 * 60 * 24 * 30 # ~= 1 month
    default_rendering_format = "html5"

    @cached_getter
    def available_languages(self):
        """The list of languages that items in the listing can be displayed in.

        Each language is represented using its two letter ISO code.

        @type: sequence of unicode
        """
        user = app.user
        return [
            language
            for language in Configuration.instance.languages
            if user.has_permission(
                ReadTranslationPermission,
                language = language
            )
        ]

    @cached_getter
    def visible_languages(self):
        return get_parameter(
            schema.Collection(
                "language",
                items = schema.String(),
                default = [get_language()]
            ),
            source = CookieParameterSource(
                cookie_naming = "visible_languages",
                cookie_duration = self.settings_duration
            )
        )

    # URIs and navigation
    #--------------------------------------------------------------------------
    def edit_uri(self, target, *args, **kwargs):
        """Get the URI of the edit page of the specified item.

        @param target: The item or content type to get the URI for.
        @type target: L{Item<woost.models.Item>} instance or class

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
            params["item_type"] = target.full_name

        # URI for existing items
        else:
            primary_member = target.__class__.primary_member

            if primary_member is None:
                raise TypeError("Can't edit types without a primary member")

            target_id = target.get(primary_member)

            if target_id is None:
                raise ValueError("Can't edit objects without an identifier")

        uri = self.contextual_uri(
            "content",
            target_id,
            *(args or ["fields"])
        )

        if params:
            uri += "?" + urlencode(
                dict((k, v) for k, v in params.iteritems() if v is not None),
                True
            )

        return uri + "#default"

    def go_back(self):
        """Redirects the user to its previous significant location."""

        edit_stack = self.edit_stack

        # Go back to the parent edit state
        if edit_stack:
            edit_stack.go_back()

        # Go back to the root of the backoffice
        else:
            redirect(
                edit_stack and edit_stack.root_url or self.contextual_uri()
            )

    # Edit stack
    #--------------------------------------------------------------------------
    @getter
    def edit_stack(self):
        """The edit stack for the current request.
        @type: L{EditStack<woost.controllers.backoffice.editstack.EditStack>}
        """
        return self.context["edit_stacks_manager"].current_edit_stack

    @getter
    def stack_node(self):
        """The top node of the edit stack for the current request.
        @type: L{StackNode<woost.controllers.backoffice.editstack.StackNode>}
        """
        stack = self.edit_stack
        return stack and stack[-1]

    @getter
    def edit_node(self):
        """The topmost edit node of the edit stack for the current request.
        @type: L{EditNode<woost.controllers.backoffice.editstack.EditNode>}
        """
        stack = self.edit_stack
        if stack:
            return stack[-1].get_ancestor_node(EditNode, include_self = True)
        return None

    @getter
    def relation_node(self):
        """The topmost relation node of the edit stack for the current request.
        @type: L{RelationNode<woost.controllers.backoffice.editstack.RelationNode>}
        """
        stack = self.edit_stack
        if stack:
            return stack[-1].get_ancestor_node(
                RelationNode,
                include_self = True
            )
        return None

    # Request flow
    #--------------------------------------------------------------------------
    @event_handler
    def handle_exception_raised(cls, event):

        # Redirect the user to the backoffice root when failing to load an edit
        # stack node
        if isinstance(
            event.exception,
            WrongEditStackError
        ):
            Notification(translations(event.exception), "error").emit()
            redirect(event.source.contextual_uri())

    def _invoke_user_action(self):

        action = self.action

        if action:

            for error in self.action_errors:
                self._handle_user_action_error(error)

            action.invoke(
                self,
                self.action_selection,
                **self.action_parameters
            )

    _graceful_user_action_errors = set([SelectionError])

    def _handle_user_action_error(self, error):
        if isinstance(error, tuple(self._graceful_user_action_errors)):
            Notification(translations(error), "error").emit()
            self.go_back()
        else:
            raise error

    @request_property
    def action_data(self):

        data = {
            "action": None,
            "selection": None,
            "schema": None,
            "parameters": {},
            "errors": []
        }

        value = cherrypy.request.params.get("action")

        if value:
            args = value.split()
            action_id = args.pop(0)
            action = get_user_action(action_id)

            if action and action.enabled:
                selection = []

                if args and ":" not in args[0]:
                    selection_value = args.pop(0)

                    if selection_value.startswith("$"):
                        selection_value = cherrypy.request.params.get(
                            selection_value[1:]
                        )

                    if selection_value:
                        cls = action.content_type
                        if not cls or isinstance(cls, tuple):
                            cls = Item

                        if isinstance(selection_value, basestring):
                            selection_value = selection_value.split(",")

                        for id in selection_value:
                            item = cls.get_instance(int(id))
                            if item:
                                selection.append(item)

                params_schema = action.get_parameters_schema(self, selection)
                parameters = data["parameters"]

                data["action"] = action
                data["selection"] = selection
                data["schema"] = params_schema

                if params_schema:
                    values = {}
                    for arg in args:
                        key, value = arg.split(":")
                        values[key] = value

                    get_parameter(
                        params_schema,
                        source = values.get,
                        target = parameters
                    )

                data["errors"].extend(
                    action.get_errors(
                        self,
                        selection,
                        params_schema,
                        **parameters
                    )
                )

        return data

    @request_property
    def action(self):
        return self.action_data["action"]

    @request_property
    def action_selection(self):
        return self.action_data["selection"]

    @request_property
    def action_schema(self):
        return self.action_data["schema"]

    @request_property
    def action_parameters(self):
        return self.action_data["parameters"]

    @request_property
    def action_errors(self):
        return self.action_data["errors"]

    @cached_getter
    def user_views(self):

        user = app.user
        views = OrderedSet()

        for role in user.iter_roles():
            views.extend(role.user_views)

        return views

    @cached_getter
    def client_side_scripting(self):
        return get_parameter(schema.Boolean("client_side_scripting"))

    @cached_getter
    def output(self):
        output = BaseCMSController.output(self)
        output.update(
            backoffice = app.publishable,
            section = self.section,
            edit_stack = self.edit_stack,
            edit_uri = self.edit_uri,
            user_views = self.user_views,
            available_languages = self.available_languages,
            visible_languages = self.visible_languages,
            client_side_scripting = self.client_side_scripting
        )
        return output


class EditStateLostError(Exception):
    """An exception raised when a user requests an edit state that is no longer
    available."""

