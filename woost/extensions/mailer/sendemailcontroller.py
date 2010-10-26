#-*- coding: utf-8 -*-
u"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			September 2010
"""
import smtplib
import cherrypy
from simplejson import dumps
from cocktail import schema
from cocktail.events import event_handler
from cocktail.modeling import cached_getter
from cocktail.controllers.location import Location
from woost.models import Site, get_current_user
from woost.models.permission import ReadPermission
from woost.controllers.backoffice.editcontroller import EditController
from woost.extensions.mailer.mailing import MAILING_FINISHED, tasks
from woost.extensions.mailer.sendemailpermission import SendEmailPermission


class SendEmailController(EditController):

    view_class = "woost.extensions.mailer.SendEmailView"
    section = "send_email"
    task_id = None

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
    def submitted(self):
        return self.action is not None or self.mailer_action is not None

    @cached_getter
    def mailer_action(self):
        return self.params.read(schema.String("mailer_action"))

    @cherrypy.expose
    def mailing_state(self, task_id, *args, **kwargs):
        cherrypy.response.headers["Content-Type"] = "application/json"

        task = tasks.get(int(task_id))
        user = get_current_user()

        if task is None:
            return dumps({})

        if not user.has_permission(ReadPermission, target = task.mailing):
            raise cherrypy.HTTPError(403, "Forbidden")

        tasks.remove_expired_tasks()

        return dumps({
            "sent": len(task.mailing.sent),
            "errors": len(task.mailing.errors),
            "total": task.mailing.total,
            "completed": task.completed
        })

    def submit(self):

        user = get_current_user()
        mailing = self.context["cms_item"]

        if not (
            mailing.is_inserted 
            and not mailing.status == MAILING_FINISHED
            and user.has_permission(SendEmailPermission)
            and user.has_permission(ReadPermission, target = mailing)
        ):
            raise cherrypy.HTTPError(403, "Forbidden")

        if self.mailer_action != "send":
            EditController.submit(self)
        else:
            self.task_id = mailing.id
            mailing._v_template_values = {
                "cms": self.context["cms"],
                "base_url": unicode(Location.get_current_host()).rstrip("/")
            }
            mailing.send(self.smtp_server, self.context.copy())

    @cached_getter
    def output(self):
        output = EditController.output(self)
        output.update(
            action = self.mailer_action,
            task_id = self.task_id
        )
        return output

