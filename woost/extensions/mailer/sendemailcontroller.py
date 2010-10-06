#-*- coding: utf-8 -*-
u"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			September 2010
"""
from __future__ import with_statement
import logging
import smtplib
import cherrypy
from threading import Thread, Lock
from simplejson import dumps
from email.mime.text import MIMEText
from email.Header import Header
from email.Utils import formatdate
from cocktail import schema
from cocktail.modeling import cached_getter
from cocktail.translations import translations, set_language
from cocktail.controllers import context
from cocktail.controllers.parameters import get_parameter
from cocktail.controllers.renderingengines import get_rendering_engine
from woost.models import (
    Role, Language, Site, get_current_user, set_current_user
)
from woost.controllers.backoffice.editcontroller \
    import EditController


logger = logging.getLogger("woost.extensions.mailer")


thread_data = {}

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


class MailerThread(Thread):
    
    subtype = "html"
    encoding = "utf-8"

    def __init__(
        self, 
        user, 
        item, 
        receivers, 
        form_data, 
        rendering_enigne_options,
        controller_context = {},
        context = {},
        *args, 
        **kwargs
    ):
        Thread.__init__(self, *args, **kwargs)
        self.user = user
        self.item = item
        self.receivers = receivers
        self.form_data = form_data
        self.rendering_enigne_options = rendering_enigne_options
        self.controller_context = controller_context
        self.context = context
        self.smtp_host = Site.main.smtp_host or "localhost"                                                                                                                                                         
        self.smtp_port = smtplib.SMTP_PORT
        self.smtp_user = Site.main.smtp_user
        self.smtp_password = Site.main.smtp_password
        self.__cached_email_content = None
        self.state = {
            "num_receivers": len(self.receivers),
            "mailer_errors": 0,
            "emails_sent": 0,
            "alive": True
        }

        # Initialize thread data
        lock = Lock()
        with lock:
            thread_data[str(id(self))] = self

    @cached_getter                                                                                                                                                                                             
    def mailer_rendering_engine(self):
        return get_rendering_engine(
            self.item.template.engine
        )

    def render_email_content(self, user, document):
        output = self.context
        output.update(
            user = user,
            publishable = document
        )

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

    def run(self):
        logger.info("Sending %s" % repr(self.item))
        logger.info("Data - %s" % self.form_data)

        cherrypy.request.config["rendering.engine_options"] = \
            self.rendering_enigne_options
        set_language(self.form_data["language"].iso_code)
        set_current_user(self.user)
        context.update(self.controller_context)

        for receiver in self.receivers:
            try:
                sender = self.form_data["sender"]
                receiver_email = receiver.email.strip()
                subject = self.form_data["subject"]

                message = MIMEText(
                    self.render_email_content(receiver, self.item),
                    _subtype = self.subtype, 
                    _charset = self.encoding
                )
                message["To"] = receiver_email
                message["From"] = sender
                message["Subject"] = Header(subject, "utf-8")
                message["Date"] = formatdate()
                # Send the message
                smtp = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.smtp_user and self.smtp_password:
                    smtp.login(
                        self.smtp_user.encode(self.encoding), 
                        self.smtp_password.encode(self.encoding)
                    )
                smtp.sendmail(sender, [receiver_email], message.as_string())
                smtp.quit()
                logger.info("Email sent to %s (%s)" % (receiver, receiver.email))
            except Exception, e:
                logger.exception("%s (%s) - %s" % (receiver, receiver.email, e))
                self.state["mailer_errors"] += 1
            finally:
                self.state["emails_sent"] += 1

        self.state["alive"] = False


class SendEmailController(EditController):

    section = "send_email"

    def __init__(self, *args, **kwargs):
        EditController.__init__(self, *args, **kwargs)
        self.thread_id = None

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

    @cherrypy.expose
    def mailing_state(self, thread_id, *args, **kwargs):
        cherrypy.response.headers["Content-Type"] = "text/javascript"

        lock = Lock()
        with lock:
            thread = thread_data.get(thread_id)
            if thread:
                data = thread.state.copy()
                user_id = thread.user.id

                # Remove dead threads
                for key, value in thread_data.items():
                    if not value.state.get("alive"):
                        del thread_data[key]
            else:
                user_id = None

        # Check permission
        if get_current_user().id != user_id:
            data = ""
        else:
            data["progress"] = (
                int(100 * data["emails_sent"] / data["num_receivers"])
            ) if data["alive"] else 100
            data["edit_stack"] = self.edit_stack.to_param()

        return dumps(data)


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
                mailer_thread = MailerThread(
                    get_current_user(), 
                    self.context["cms_item"], 
                    self.mailer_receivers, 
                    self.form_data,
                    cherrypy.request.config.get("rendering.engine_options"),
                    controller_context = context.copy(),
                    context = {
                        "cms": self.context["cms"], 
                        "base_url": "http://" + cherrypy.url().split('/')[2]
                    }
                )
                self.thread_id = id(mailer_thread)
                mailer_thread.start()

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
            thread_id = self.thread_id
        )
        return output

