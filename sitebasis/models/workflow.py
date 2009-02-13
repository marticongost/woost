#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""


class Item(...):

    state = schema.Reference(
        type = "sitebasis.models.State"
    )


class Workflow(Item):

    title = schema.String(
        unique = True,
        required = True,
        translated = True
    )

    states = schema.Collection(
        items = "sitebasis.models.State",
        bidirectional = True
    )


class State(Item):
 
    title = schema.String(
        unique = True,
        required = True,
        translated = True
    )

    workflow = schema.Reference(
        type = "sitebasis.models.Workflow"
        bidirectional = True
    )


class WorkflowRule(AccessRule):
    
    source_workflow = schema.Reference(
        type = "sitebasis.models.Workflow"
    )

    source_state = schema.Reference(
        type = "sitebasis.models.State"
    )

    target_workflow = schema.Reference(
        type = "sitebasis.models.Workflow"
    )

    target_state = schema.Reference(
        type = "sitebasis.models.State"
    )

