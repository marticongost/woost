#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
import re
import buffet
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
        exec code in context

class SendEmailTriggerResponse(TriggerResponse):
    """A trigger response that allows to send an email."""

    instantiable = True
    members_order = "template_engine", "sender", "receivers", "subject", "body"

    template_engine = schema.String(
        required = True,
        enumeration = buffet.available_engines.keys()
    )

    sender = schema.String(
        required = True,
        edit_control = "cocktail.html.TextArea"
    )

    receivers = schema.String(
        required = True,
        edit_control = "cocktail.html.TextArea"
    )

    subject = schema.String(
        required = True,
        edit_control = "cocktail.html.TextArea"
    )

    body = schema.String(
        required = True,
        edit_control = "cocktail.html.TextArea"
    )

    def execute(self, item, action, agent, batch = False, **context):

        import smtplib
        from sitebasis.models import Site
        from email.mime.text import MIMEText
        from email.Utils import formatdate

        smtp_host = Site.main.smtp_host or "localhost"
        smtp_port = smtplib.SMTP_PORT
        mime_type = "html"

        context.update(
            item = item,
            action = action,
            agent = agent,
            batch = batch
        )

        template_engine = buffet.available_engines[self.engine]
        engine = template_engine()

        def render(field_name):
            template = engine.load_template(field_name, self.get(field_name))
            try:
                return engine.render(context, template = template)
            except NameError:
                raise NameError("Error in %s template" % field_name)

        subject = render("subject")
        sender = render("sender")
        receivers = render("receivers").split()
        body = render("body")

        message = MIMEText(body, mime_type)
        message["Subject"] = subject
        message["From"] = sender
        message["To"] = receivers
        message["Date"] = formatdate()

        smtp = smtplib.SMTP(smtp_host, smtp_port)
        smtp.sendmail(sender, receivers, message.as_string())
        smtp.quit()

# TODO: Implement other response types:
# NotifyUserTriggerResponse
# SendXMPPTriggerResponse (as an extension?)
# SendSMSTriggerResponse (as an extension?)
# WriteLogTriggerResponse (as an extension?)
# SetStateTriggerResponse (as part of the workflow extension)

