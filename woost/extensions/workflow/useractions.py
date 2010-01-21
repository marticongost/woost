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
from cocktail.controllers import get_parameter, context as controller_context
from cocktail.controllers.viewstate import view_state
from cocktail.html import Element
from woost.models import (
    get_current_user,
    ReadPermission,
    ModifyPermission
)
from woost.controllers.backoffice.useractions import UserAction
from woost.controllers.backoffice.itemfieldscontroller \
    import ItemFieldsController
from woost.controllers.backoffice.collectioncontroller \
    import CollectionController
from woost.extensions.workflow.transitionpermission import \
    TransitionPermission
from woost.extensions.workflow.transition import Transition


class TransitionAction(UserAction):
 
    included = frozenset(["item_buttons"])
    excluded = frozenset(["new_item"])

    def is_available(self, context, target):
 
        # Hide the transition action unless there are one or more available
        # outgoing states for the item's current condition
        return UserAction.is_available(self, context, target) \
            and bool(self._get_outgoing_transitions(target))
    
    def get_dropdown_panel(self, item):
        
        panel = Element()

        for transition in self._get_outgoing_transitions(item):
            
            button = Element("a")

            # Transitions with parameters: redirect to the transition form
            if transition.transition_form:
                button["href"] = controller_context["cms"].contextual_uri(
                    "workflow_transition",
                    item = item.id,
                    transition = transition.id
                )

            # This should really be a POST operation, but HTML doesn't provide
            # multi-value buttons, so regular links and GET requests are all
            # that is left :(
            else:
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
        user = get_current_user()
        user.require_permission(
            TransitionPermission,
            target = item,
            transition = transition
        )

        # Transition the item to its new state
        transition.execute(item)
        controller.notify_user(
            translations(
                "woost.controllers.backoffice.useractions.TransitionAction"
                " state set",
                item = item
            ),
            "success"
        )
        datastore.commit()

        # GET redirection, to avoid duplicate POST requests. Also, permissions
        # that allowed the user to edit or view the transitioned item may no
        # longer apply (as they may have been granted by the item's previous
        # state). If that is the case, redirect the user to the best available
        # view
        cms = controller.context["cms"]
        url = None

        if isinstance(
            controller,
            (ItemFieldsController, CollectionController)
        ):
            if not user.has_permission(ModifyPermission, target = item):
                if user.has_permission(ReadPermission, target = item):
                    url = controller.edit_uri(item, "show_detail")
                else:
                    url = cms.contextual_uri()

        elif not user.has_permission(ReadPermission, target = item):
            url = cms.contextual_uri()

        raise cherrypy.HTTPRedirect(
            url or "?" + view_state(item_action = None, transition = None)
        )

TransitionAction("transition").register(before = "close")

