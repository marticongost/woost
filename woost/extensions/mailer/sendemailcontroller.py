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
from simplejson import dumps
from email.mime.text import MIMEText
from email.Header import Header
from email.Utils import formatdate
from cocktail.asynctask import TaskManager
from cocktail import schema
from cocktail.modeling import cached_getter
from cocktail.translations import translations, set_language
from cocktail.controllers import context
from cocktail.controllers.parameters import get_parameter
from woost.models import (
    Role, Language, Site, get_current_user, set_current_user
)
from woost.controllers.backoffice.editcontroller import EditController
from woost.extensions.mailer.sendemailpermission import SendEmailPermission

logger = logging.getLogger("woost.extensions.mailer")

tasks = TaskManager()

def get_receivers_by_roles(roles):
    users = set()
    for role in roles:
        users.update(
            user for user in role.users
            if user.enabled
            and getattr(user, "confirmed_email", True)
        )

    return users


class Mailing(object):

    errors = 0
    sent = 0    
    smtp = None
    document = None
    receivers = []
    sender = None
    subject = None
    customizable = False
    template_values = {}
    __cached_body = None

    def __init__(self):
        self.receivers = []
        self.template_values = {}

    def send(self):
        logger.info("Sending mailing")

        for receiver in self.receivers:
            try:                
                message = MIMEText(
                    self.render_body(receiver),
                    _subtype = self.document.mime_type.split("/")[1],
                    _charset = self.document.encoding
                )
                message["To"] = receiver.email
                message["From"] = self.sender
                message["Subject"] = Header(self.subject, self.document.encoding)
                message["Date"] = formatdate()
                self.smtp.sendmail(self.sender, [receiver.email], message.as_string())
                logger.info("Email sent to %s (%s)" % (receiver, receiver.email))
            except Exception, e:
                logger.exception("%s (%s) - %s" % (receiver, receiver.email, e))
                self.errors += 1
            finally:
                self.sent += 1

    def render_body(self, receiver):
        
        if not self.customizable and self.__cached_body:
            return self.__cached_body

        values = self.template_values
        
        if self.customizable:
            values = values.copy()
            values["mailing_receiver"] = receiver
        
        body = self.document.render(**values)

        if not self.customizable:
            self.__cached_body = body

        return body


class SendEmailController(EditController):

    section = "send_email"
    task_id = None

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
                        enumeration = lambda ctx: self.available_roles,
                        translate_value = lambda value, language = None, **kwargs: \
                            "%s (%d %s)" % (
                                translations(value),
                                len(get_receivers_by_roles([value])),
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

    @cached_getter
    def available_roles(self):
        roles = []
        user = get_current_user()
        for role in Role.select():
            if user.has_permission(SendEmailPermission, role = role) \
            and len(get_receivers_by_roles([role])):
                roles.append(role)
        return roles

    # Mailing
    #------------------------------------------------------------------------------

    @cached_getter
    def mailing(self):
        mailing = Mailing()
        mailing.smtp = self.smtp_server
        mailing.document = self.context["cms_item"]
        mailing.receivers = self.mailer_receivers
        mailing.sender = self.form_data["sender"]
        mailing.subject = self.form_data["subject"]
        mailing.customizable = self.form_data.get("per_user_customizable", False)
        mailing.template_values = {
            "cms": self.context["cms"],
            "base_url": "http://" + cherrypy.url().split('/')[2]
        }
        return mailing

    @cached_getter
    def smtp_server(self):

        site = Site.main
        smtp = smtplib.SMTP(site.smtp_host, smtplib.SMTP_PORT)

        if site.smtp_user and site.smtp_password:
            smtp.login(
                str(site.smtp_user),
                str(site.smtp_password)
            )

        return smtp

    @cached_getter
    def mailer_action(self):
        return self.params.read(schema.String("mailer_action"))

    @cached_getter
    def mailer_receivers(self):
        return get_receivers_by_roles(self.form_data.get("roles", []))

    @cherrypy.expose
    def mailing_state(self, task_id, *args, **kwargs):
        cherrypy.response.headers["Content-Type"] = "application/json"

        task = tasks.get(int(task_id))

        if task is None:
            return dumps({})
        
        if get_current_user().id != task.user_id:
            raise cherrypy.HTTPError("403 Forbidden")

        tasks.remove_expired_tasks()

        return dumps({
            "sent": task.mailing.sent,
            "errors": task.mailing.errors,
            "total": len(task.mailing.receivers),
            "completed": task.completed
        })

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
                
                user = get_current_user()
                language = self.form_data["language"].iso_code
                current_context = context.copy()
                mailing = self.mailing
                
                def process():
                    set_current_user(user)
                    set_language(language)
                    context.update(current_context)
                    mailing.send()

                task = tasks.execute(process)
                task.mailing = mailing
                task.user_id = user.id
                self.task_id = task.id


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
            task_id = self.task_id
        )
        return output

