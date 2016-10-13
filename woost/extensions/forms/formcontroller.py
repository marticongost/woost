#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from datetime import datetime
from cocktail.translations import translations
from cocktail.modeling import extend, call_base
from cocktail.controllers import (
    Controller,
    FormProcessor,
    request_property,
    context,
    redirect
)
from woost import app
from woost.controllers.uploadform import UploadForm
from woost.controllers.formagreement import requires_agreement

translations.load_bundle("woost.extensions.forms.formcontroller")


class FormController(FormProcessor, Controller):

    is_transactional = True

    class UserForm(UploadForm):

        def __init__(self, *args, **kwargs):
            UploadForm.__init__(self, *args, **kwargs)
            for agreement in self.controller.block.agreements:
                agreement_member = requires_agreement(
                    self,
                    name = "agreement%d" % agreement.id,
                    document = agreement.document
                )
                if agreement.text:
                    agreement.custom_translation_key = \
                        "woost.extensions.forms.formcontroller.form_agreement"

        @property
        def model(self):
            return self.controller.block.form_model

        @request_property
        def adapter(self):
            adapter = UploadForm.adapter(self)
            adapter.exclude("submit_date")
            return adapter

        def submit(self):
            UploadForm.submit(self)
            self.instance["submit_date"] = datetime.now()
            block = self.controller.block

            # User supplied initialization
            if block.submit_code:
                submit_context = {
                    "form": self,
                    "block": block
                }
                label = "%s #%s.submit_code" % (
                    block.__class__.__name__,
                    block.id
                )
                code = compile(block.submit_code, label, "exec")
                exec code in submit_context

            # Do something with the received data (by default, store it)
            self.handle_submitted_data()

        def handle_submitted_data(self):
            self.controller.block.submitted_data.append(self.instance)

        def after_submit(self):
            block = self.controller.block
            notification_receivers = block.notification_receivers
            email_messages = block.email_messages
            redirection_dest = block.redirection
            redirection_parameters = {}

            # User supplied initialization
            if block.after_submit_code:
                after_submit_context = {
                    "form": self,
                    "block": block,
                    "notification_receivers": notification_receivers,
                    "email_messages": email_messages,
                    "redirection": redirection_dest,
                    "redirection_parameters": redirection_parameters
                }
                label = "%s #%s.after_submit_code" % (
                    block.__class__.__name__,
                    block.id
                )
                code = compile(block.after_submit_code, label, "exec")
                exec code in after_submit_context
                notification_receivers = \
                    after_submit_context["notification_receivers"]
                email_messages = after_submit_context["email_messages"]
                redirection_dest = after_submit_context["redirection"]
                redirection_parameters = \
                    after_submit_context["redirection_parameters"]

            # E-mail notifications
            for message in email_messages:
                message.send({
                    "block": block,
                    "form_data": self.instance,
                    "form_schema": self.model,
                    "notification_receivers": notification_receivers
                })

            # Redirection
            if redirection_dest is None:
                publishable = app.publishable
                redirection_dest = \
                    publishable.find_first_child_redirection_target()

            if redirection_dest is not None:
                redirect(
                    redirection_dest.get_uri(
                        parameters = redirection_parameters
                    )
                )

