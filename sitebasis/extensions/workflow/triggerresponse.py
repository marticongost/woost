#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			June 2009
"""
from cocktail import schema
from cocktail.persistence import datastore
from sitebasis.models.triggerresponse import TriggerResponse
from sitebasis.extensions.workflow.state import State

class SetStateTriggerResponse(TriggerResponse):
    """A trigger response that allows to change an Item state."""
    instantiable = True

    target_state = schema.Reference(
        type = State,
	    required = True,
	    related_end = schema.Collection(cascade_delete = True),
        edit_control = "cocktail.html.DropdownSelector"
    )

    def execute(self, items, action, agent, batch = False, **context):
        for item in items:
            item.state = self.target_state

