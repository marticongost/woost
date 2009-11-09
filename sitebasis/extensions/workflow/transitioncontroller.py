#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2009
"""
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.events import event_handler
from cocktail.pkgutils import import_object
from cocktail.translations import translations
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.controllers import (
    get_parameter,
    FormControllerMixin
)
from sitebasis.models import (
    Item,
    get_current_user
)
from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from sitebasis.extensions.workflow.transition import Transition
from sitebasis.extensions.workflow.transitionpermission \
    import TransitionPermission


class TransitionController(FormControllerMixin, BaseBackOfficeController):

    view_class = "sitebasis.extensions.workflow.TransitionView"

    @event_handler
    def handle_traversed(cls, event):
        controller = event.source        
        get_current_user().require_permission(
            TransitionPermission,
            target = controller.item,
            transition = controller.transition
        )

    @cached_getter
    def item(self):
    
        item = get_parameter(schema.Reference("item", type = Item))

        if item is None or item.workflow_state is None:
            raise ValueError("Invalid item selected")

        return item

    @cached_getter
    def transition(self):

        transition = get_parameter(
            schema.Reference("transition", type = Transition)
        )

        if transition is None \
        or transition not in self.item.workflow_state.outgoing_transitions:
            raise ValueError("Invalid transition selected")

        return transition

    @cached_getter
    def form_model(self):
        return import_object(self.transition.transition_form)

    def submit(self):
        
        item = self.item

        if "submit" in cherrypy.request.params:

            # Apply form data
            FormControllerMixin.submit(self)

            # Execute the transition
            transition = self.transition
            transition.execute(item, data = self.form_instance)
            datastore.commit()

            # Inform the user of the result
            self.notify_user(
                translations(
                    "sitebasis.controllers.backoffice.useractions.TransitionAction"
                    " state set",
                    item = item
                ),
                "success"
            )
        
        # Redirect the user to the transitioned item's edit form
        raise cherrypy.HTTPRedirect(self.edit_uri(item))

    @cached_getter
    def output(self):
        output = BaseBackOfficeController.output(self)
        output.update(
            item = self.item,
            transition = self.transition
        )
        return output

