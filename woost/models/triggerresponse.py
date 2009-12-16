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
from cocktail.html.datadisplay import display_factory
from woost.models.item import Item

line_separator_expr = re.compile("[\r\n]+")


class TriggerResponse(Item):
    """A response action, to be executed when invoking the
    L{trigger<woost.models.Trigger>} it is bound to."""
    
    integral = True
    instantiable = False
    visible_from_root = False

    trigger = schema.Reference(   
        type = "woost.models.Trigger",
        visible = False,
        bidirectional = True,
        integral = False
    )

    @abstractmethod
    def execute(self, items, user, batch = False, **context):
        """Executes the response with the supplied context.
        
        This method will be called when the response's trigger conditions are
        met. Subclasses of trigger response are expected to override this
        method in order to implement their particular logic.

        @param items: The list of items that received the condition that
            triggered the response.
        @type items: L{Item<woost.models.item.Item>} list

        @param user: The user that triggered the response.
        @type user: L{User<woost.models.user.User>}

        @param batch: Indicates if the response is being executed by a trigger
            that is set to operate in L{batch mode
            <woost.models.Trigger.batch>}.
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
        edit_control = display_factory(
            "cocktail.html.CodeEditor", syntax = "python"
        )
    )

    def execute(self, items, user, batch = False, **context):
        context.update(
            items = items,
            user = user,
            batch = batch
        )
        code = line_separator_expr.sub("\n", self.code)
        exec code in context


class SendEmailTriggerResponse(TriggerResponse):
    """A trigger response that allows to send an email."""

    instantiable = True
    members_order = [
        "template_engine",
        "sender",
        "receivers",
        "bcc",
        "subject",
        "body"
    ]

    template_engine = schema.String(
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
    
    bcc = schema.String(
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

    def execute(self, items, user, batch = False, **context):

        import smtplib
        from woost.models import Site
        from email.mime.text import MIMEText
        from email.Utils import formatdate

        smtp_host = Site.main.smtp_host or "localhost"
        smtp_port = smtplib.SMTP_PORT
        mime_type = "html"

        context.update(
            items = items,
            user = user,
            batch = batch
        )

        if self.template_engine:
            template_engine = buffet.available_engines[self.template_engine]
            engine = template_engine(
                options = {"mako.output_encoding": "utf-8"}
            )

            def render(field_name):
                markup = self.get(field_name)
                if markup:
                    template = engine.load_template(
                        field_name,
                        self.get(field_name)
                    )
                    try:
                        return engine.render(context, template = template)
                    except NameError:
                        raise NameError("Error in %s template" % field_name)
                else:
                    return u""
           
            subject = render("subject").strip()
            sender = render("sender").strip()
            bcc = render("bcc").strip()
            receivers = render("receivers").strip()
            body = render("body")
        else:
            subject = self.subject
            sender = self.sender
            bcc = self.bcc
            receivers = self.receivers
            body = self.body

        receivers_set = set(r.strip() for r in receivers.split())
        
        if bcc:
            receivers_set.update(r.strip() for r in bcc.split())

        if receivers_set:
            message = MIMEText(body, mime_type)
            message["Subject"] = subject
            message["From"] = sender
            message["To"] = receivers
            message["Date"] = formatdate()

            smtp = smtplib.SMTP(smtp_host, smtp_port)
            smtp.sendmail(sender, list(receivers_set), message.as_string())
            smtp.quit()

# TODO: Implement other response types:
# NotifyUserTriggerResponse
# SendXMPPTriggerResponse (as an extension?)
# SendSMSTriggerResponse (as an extension?)
# WriteLogTriggerResponse (as an extension?)
# SetStateTriggerResponse (as part of the workflow extension)

