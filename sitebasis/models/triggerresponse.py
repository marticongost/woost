#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
import re
from cocktail.modeling import abstractmethod
from cocktail import schema
from sitebasis.models.item import Item

line_separator_expr = re.compile("[\r\n]+")


class TriggerResponse(Item):
    """A response action, to be executed when invoking the
    L{trigger<sitebasis.models.Trigger>} it is bound to."""
    
    integral = True
    instantiable = False

    trigger = schema.Reference(   
        type = "sitebasis.models.Trigger",
        visible = False,
        bidirectional = True,
        integral = False
    )

    @abstractmethod
    def execute(self, item, action, agent, batch = False, **context):
        """Executes the response with the supplied context.
        
        This method will be called when the response's trigger conditions are
        met. Subclasses of trigger response are expected to override this
        method in order to implement their particular logic.

        @param item: The item that received the condition that triggered the
            response.
        @type item: L{Item<sitebasis.models.item.Item>}

        @param action: The kind of the action that triggered the response.
        @type action: L{Action<sitebasis.models.Action>}

        @param agent: The agent (user) that triggered the response.
        @type agent: L{Agent<sitebasis.models.Agent>}

        @param batch: Indicates if the response is being executed by a trigger
            that is set to operate in L{batch mode
            <sitebasis.models.Trigger.batch>}.
        @type batch: bool

        @param context: Additional context. Available keys depend on the kind
            of action that triggered the response.        
        """
        

class CustomTriggerResponse(TriggerResponse):
    """A trigger response that allows the execution of arbitrary python
    code."""
    instantiable = True

    code = schema.String(
        required = True,
        edit_control = "cocktail.html.TextArea"
    )

    def execute(self, item, action, agent, batch = False, **context):
        context.update(
            item = item,
            action = action,
            agent = agent,
            batch = batch
        )
        code = line_separator_expr.sub("\n", self.code)
        code = "raise ValueError('Foo')"
        exec code in context


# TODO: Implement other response types:
# NotifyUserTriggerResponse
# SendXMPPTriggerResponse (as an extension?)
# SendEmailTriggerResponse (as an extension?)
# SendSMSTriggerResponse (as an extension?)
# WriteLogTriggerResponse (as an extension?)
# SetStateTriggerResponse (as part of the workflow extension)

