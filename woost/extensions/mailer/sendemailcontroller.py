#-*- coding: utf-8 -*-
u"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			September 2010
"""
import logging
import smtplib
import cherrypy
from email.mime.text import MIMEText
from email.Header import Header
from email.Utils import formatdate
from cocktail import schema
from cocktail.modeling import cached_getter
from cocktail.translations import translations
from cocktail.controllers import context
from cocktail.controllers.parameters import get_parameter
from cocktail.controllers.renderingengines import get_rendering_engine
from woost.models import Role, Language, Site
from woost.controllers.backoffice.editcontroller \
    import EditController


logger = logging.getLogger("woost.extensions.mailer")


def available_users(roles):
    users = []
    for role in roles:
        users.extend([
            user for user in role.users 
            if user.enabled
            and getattr(user, "confirmed_email", True)
        ])

    return users

def _available_roles():
    roles = []
    for role in Role.select():
        if role.qname != "woost.anonymous" \
        and len(available_users([role])):
            roles.append(role)
    return roles


class SendEmailController(EditController):

    section = "send_email"
    subtype = "html"
    encoding = "utf-8"

    def __init__(self, *args, **kwargs):
        EditController.__init__(self, *args, **kwargs)
        self.mailer_errors = 0
        self.__cached_email_content = None

    # Form
    #------------------------------------------------------------------------------

    @cached_getter                                                                                                                                                                                             
    def form_submitted(self):
        return self.mailer_action in ("continue", "send")

    @cached_getter
    def form_schema(self):
        form_schema = schema.Schema(
            "SendEmail",
            members = [
                schema.String(
                    "sender",
                    required = True,
                    format = r"([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)"
                ),
                schema.String(
                    "subject",
                    required = True
                ),
                schema.Reference(
                    "language",
                    type = "woost.models.Language",
                    required = True,
                    enumeration = lambda ctx: \
                        [
                            Language.get_instance(iso_code = language) 
                            for language in self.context["cms_item"].translations.keys()
                        ],
                ),
                schema.Collection(
                    "roles",
                    items = schema.Reference(
                        type = "woost.models.Role", 
                        default_order = "title",
                        enumeration = lambda ctx: _available_roles(),
                        translate_value = lambda value, language = None, **kwargs: \
                            "%s (%d %s)" % (
                                translations(value), 
                                len(available_users([value])),
                                translations("woost.extensions.mailer users")
                            )
                    ),
                    min = 1,
                    edit_inline = True
                )
            ]
        )

        if self.context["cms_item"].template.per_user_customizable:
            form_schema.add_member(
                schema.Boolean(
                    "per_user_customizable",
                    default = True
                )
            )

        return form_schema

    @cached_getter
    def form_data(self):
        form_data = {}
        get_parameter(
            self.form_schema,
            target = form_data,
            errors = "ignore",
            undefined = "skip"
        )
        return form_data

    @cached_getter
    def form_errors(self):                                                                                                                                                                                     
        return schema.ErrorList(
            self.form_schema.get_errors(
                self.form_data
            )
            if self.form_submitted
            else ()
        )

    # Mailing
    #------------------------------------------------------------------------------

    @cached_getter                                                                                                                                                                                             
    def mailer_action(self):
        return self.params.read(schema.String("mailer_action"))

    @cached_getter                                                                                                                                                                                             
    def mailer_receivers(self):
        return set(available_users(self.form_data.get("roles", [])))

    @cached_getter                                                                                                                                                                                             
    def mailer_rendering_engine(self):
        return get_rendering_engine(
            self.context["cms_item"].template.engine
        )

    def send(self):
        smtp_host = Site.main.smtp_host or "localhost"                                                                                                                                                         
        smtp_port = smtplib.SMTP_PORT
        smtp_user = Site.main.smtp_user
        smtp_password = Site.main.smtp_password

        logger.info("Sending %s" % translations(self.context["cms_item"]))
        logger.info("Data - %s" % self.form_data)

        for receiver in self.mailer_receivers:
            try:
                sender = self.form_data["sender"]
                receiver_email = receiver.email.strip()
                subject = self.form_data["subject"]

                message = MIMEText(
                    self.render_email_content(receiver, self.context["cms_item"]),
                    _subtype = self.subtype, 
                    _charset = self.encoding
                )
                message["To"] = receiver_email
                message["From"] = sender
                message["Subject"] = Header(subject, "utf-8")
                message["Date"] = formatdate()
                # Send the message
                smtp = smtplib.SMTP(smtp_host, smtp_port)
                if smtp_user and smtp_password:
                    smtp.login(
                        smtp_user.encode(self.encoding), 
                        smtp_password.encode(self.encoding)
                    )
                smtp.sendmail(sender, [receiver_email], message.as_string())
                smtp.quit()
                logger.info("Email sent to %s (%s)" % (receiver, receiver.email))
            except Exception, e:
                logger.error("%s (%s) - %s" % (receiver, receiver.email, e))
                self.mailer_errors += 1

    def render_email_content(self, user, document):
        output = {
            "user": user,
            "publishable": document,
            "cms": self.context["cms"]
        }

        if not self.form_data.get("per_user_customizable") \
        and self.__cached_email_content:
            email_content = self.__cached_email_content
        else:
            email_content = self.mailer_rendering_engine.render(
                output,
                template = document.template.identifier
            )
            self.__cached_email_content = email_content

        return email_content


    # BackOffice
    #------------------------------------------------------------------------------

    @cached_getter
    def view_class(self):
        return self.stack_node.item.send_email_view

    @cached_getter                                                                                                                                                                                             
    def ready(self):
        return EditController.ready(self) or (
            self.form_submitted and not
            self.form_errors
        )

    def submit(self):
        if not self.form_submitted:
            EditController.submit(self)
        else:
            if self.mailer_action == "send":
                self.send()

    @cached_getter
    def output(self):
        output = EditController.output(self)
        output.update(
            form_data = self.form_data,
            form_schema = self.form_schema,
            form_errors = self.form_errors,
            form_submitted = self.form_submitted,
            action = self.mailer_action,
            mailer_receivers = len(self.mailer_receivers),
            mailer_errors = self.mailer_errors
        )
        return output

