#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2010
"""
import buffet
import smtplib
from email.mime.text import MIMEText
from email.Header import Header
from email.Utils import formatdate
from cocktail import schema
from cocktail.html.datadisplay import display_factory
from woost.models import Item, Site


class EmailTemplate(Item):

    visible_from_root = False

    members_order = [
        "title",
        "mime_type",
        "sender",
        "receivers",
        "bcc",
        "template_engine",
        "subject",
        "body"
    ]

    title = schema.String(
        listed_by_default = False,
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        translated = True
    )

    mime_type = schema.String(
        required = True,
        default = "text/html",
        listed_by_default = False,
        enumeration = [
            "text/plain",
            "text/html"
        ]
    )

    sender = schema.String(
        edit_control = display_factory(
            "cocktail.html.CodeEditor", syntax = "python"
        )
    )

    receivers = schema.String(
        required = True,
        edit_control = display_factory(
            "cocktail.html.CodeEditor", syntax = "python"
        )
    )
    
    bcc = schema.String(
        listed_by_default = False,
        edit_control = display_factory(
            "cocktail.html.CodeEditor", syntax = "python"
        )
    )

    template_engine = schema.String(
        enumeration = buffet.available_engines.keys()
    )

    subject = schema.String(
        translated = True,
        edit_control = "cocktail.html.TextArea"
    )

    body = schema.String(    
        translated = True,
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea"
    )

    def send(self, context = None):

        smtp_host = Site.main.smtp_host or "localhost"
        smtp_port = smtplib.SMTP_PORT
        smtp_user = Site.main.smtp_user
        smtp_password = Site.main.smtp_password

        if context is None:
            context = {}
        
        def eval_member(key):
            expr = self.get(key)
            return eval(expr, context.copy()) if expr else None

        # MIME block
        mime_type = self.mime_type
        pos = mime_type.find("/")

        if pos != -1:
            mime_type = mime_type[pos + 1:]

        message = MIMEText("", _subtype = mime_type, _charset = "utf-8")

         # Receivers (python expression)
        receivers = eval_member("receivers")
        if receivers:
            receivers = set(r.strip() for r in receivers) 

        if not receivers:
            return set()
 
        message["To"] = ", ".join(receivers)

        # Sender (python expression)
        sender = eval_member("sender")
        if sender:
            message["From"] = sender

        # BCC (python expression)
        bcc = eval_member("bcc")
        if bcc:
            receivers.update(r.strip() for r in bcc)

        # Subject and body (templates)
        if self.template_engine:
            template_engine = buffet.available_engines[self.template_engine]
            engine = template_engine(
                options = {"mako.output_encoding": "utf-8"}
            )

            def render(field_name):
                markup = self.get(field_name)
                if markup:
                    template = engine.load_template(
                        "EmailTemplate." + field_name,
                        self.get(field_name)
                    )
                    return engine.render(context, template = template)                    
                else:
                    return u""
           
            subject = render("subject").strip()
            body = render("body")
        else:
            subject = self.subject
            body = self.body
            
        if subject:
            message["Subject"] = Header(subject, "utf-8")

        message["Date"] = formatdate()
        message.set_payload(body)

        # Send the message
        smtp = smtplib.SMTP(smtp_host, smtp_port)
        if smtp_user and smtp_password:
            smtp.login(
                smtp_user.encode('utf-8'), 
                smtp_password.encode('utf-8')
            )
        smtp.sendmail(sender, list(receivers), message.as_string())
        smtp.quit()

        return receivers

    def __translate__(self, language, **kwargs):
        return (self.draft_source is None and self.get("title", language)) \
            or Item.__translate__(self, language, **kwargs)

