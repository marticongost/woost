#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
import cherrypy
from cocktail.translations import translations
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.controllers import context as controller_context, get_parameter
from cocktail.controllers.viewstate import view_state
from cocktail.html import Element
from sitebasis.controllers.backoffice.useractions import UserAction
from sitebasis.models import allowed
from sitebasis.extensions.workflow.state import State


class TransitionAction(UserAction):
 
    included = frozenset(["item_buttons"])
    excluded = frozenset()

    def is_available(self, context, target):
 
        # Hide the transition action unless there are one or more available
        # outgoing states for the item's current condition
        if UserAction.is_available(self, context, target):
            for state in self._get_outgoing_states(target):
                return True

        return False

    def get_dropdown_panel(self, target):
        
        panel = Element()

        for state in self._get_outgoing_states(target):
            # This should really be a POST operation, but HTML doesn't provide
            # multi-value buttons, so regular links and GET requests are all
            # that is left :(
            button = Element("a")
            button["href"] = u"?" + view_state(
                new_state = state.id,
                item_action = "transition"
            )
            button.append(translations(state))            
            panel.append(button)

        return panel

    def _get_outgoing_states(self, target, restricted = True):
        if target.state is None:
            states = State.select()
        else:
            states = target.state.outgoing

        if restricted:
            user = controller_context["cms"].authentication.user
            states = (
                state
                for state in states
                if allowed(
                    user = user,
                    target_instance = target,
                    action = "transition",
                    target_new_state = state
                )
            )

        return states

    def invoke(self, controller, selection):
        
        item = selection[0]

        # Retrieve and validate the desired state for the item
        new_state = get_parameter(
            schema.Reference(
                "new_state",
                type = State,
                enumeration = self._get_outgoing_states(
                    item,
                    restricted = False
                )
            ),
            strict = True
        )

        if new_state is None:
            raise ValueError("Wrong state identifier")

        # Authorization check
        controller.restrict_access(
            target_instance = item,
            action = "transition",
            target_new_state = new_state
        )

        # Transition the item to its new state
        item.state = new_state
        controller.notify_user(
            translations(
                "sitebasis.controllers.backoffice.useractions.TransitionAction"
                " state set",
                item = item
            ),
            "success"
        )
        datastore.commit()

        raise cherrypy.HTTPRedirect(
            "?" + view_state(item_state = None, new_state = None)
        )

TransitionAction("transition").register(before = "close")

