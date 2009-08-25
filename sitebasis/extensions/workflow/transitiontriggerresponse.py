#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			Aug 2009
"""
from cocktail import schema
from cocktail.persistence import datastore
from sitebasis.models.triggerresponse import TriggerResponse
from sitebasis.extensions.workflow.transition import Transition

class TransitionTriggerResponse(TriggerResponse):
    """A trigger response that allows to change an Item state."""
    instantiable = True

    target_state = schema.Reference(
        type = Transition,
	    required = True,
	    related_end = schema.Collection(cascade_delete = True),
        edit_control = "cocktail.html.DropdownSelector"
    )

    def execute(self, items, action, user, batch = False, **context):
        transition = self.transition
        for item in items:
            transition.execute(item)

