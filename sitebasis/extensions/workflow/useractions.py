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
from cocktail.controllers import get_parameter
from cocktail.controllers.viewstate import view_state
from cocktail.html import Element
from sitebasis.models import get_current_user
from sitebasis.controllers.backoffice.useractions import UserAction
from sitebasis.extensions.workflow.transitionpermission import \
    TransitionPermission
from sitebasis.extensions.workflow.transition import Transition


class TransitionAction(UserAction):
 
    included = frozenset(["item_buttons"])
    excluded = frozenset()

    def is_available(self, context, target):
 
        # Hide the transition action unless there are one or more available
        # outgoing states for the item's current condition
        return UserAction.is_available(self, context, target) \
            and bool(self._get_outgoing_transitions(target))
    
    def get_dropdown_panel(self, item):
        
        panel = Element()

        for transition in self._get_outgoing_transitions(item):
            # This should really be a POST operation, but HTML doesn't provide
            # multi-value buttons, so regular links and GET requests are all
            # that is left :(
            button = Element("a")
            button["href"] = u"?" + view_state(
                transition = transition.id,
                item_action = "transition"
            )
            button.append(translations(transition))            
            panel.append(button)

        return panel

    def _get_outgoing_transitions(self, item, restricted = True):

        if item.workflow_state is None:
            transitions = []
        else:
            transitions = item.workflow_state.outgoing_transitions

        if restricted:
            user = get_current_user()
            transitions = [
                transition
                for transition in transitions
                if user.has_permission(
                    TransitionPermission,
                    target = item,
                    transition = transition
                )
            ]

        return transitions

    def invoke(self, controller, selection):
        
        item = selection[0]

        # Retrieve and validate the desired transition for the item
        transition = get_parameter(
            schema.Reference(
                "transition",
                type = Transition,
                enumeration = self._get_outgoing_transitions(
                    item,
                    # This allows to discriminate between invalid ids and authz
                    # errors:
                    restricted = False
                )
            ),
            strict = True
        )

        if transition is None:
            raise ValueError("Wrong transition identifier")

        # Authorization check
        get_current_user().require_permission(
            TransitionPermission,
            target = item,
            transition = transition
        )

        # Transition the item to its new state
        transition.execute(item)
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
            "?" + view_state(transition = None)
        )

TransitionAction("transition").register(before = "close")

