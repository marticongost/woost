#-*- coding: utf-8 -*-
"""Defines the `PasswordChangeConfirmationController` class.

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
import cherrypy
from cocktail import schema
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail.controllers import (
    request_property,
    get_parameter,
    FormProcessor,
    Form
)
from cocktail.controllers.fieldconfirmation import field_confirmation
from woost import app
from woost.models.user import User
from woost.controllers.publishablecontroller import PublishableController
from woost.controllers.passwordchangecontroller import generate_confirmation_hash

translations.load_bundle("woost.controllers.passwordchangeconfirmationcontroller")


class PasswordChangeConfirmationController(FormProcessor, PublishableController):

    is_transactional = True
    class_view = "woost.views.PasswordChangeFormTemplate"

    @event_handler
    def handle_traversed(cls, e):

        controller = e.source

        # Make sure we are given a user
        if controller.user is None:
            raise cherrypy.HTTPError(400, "Invalid user")

        # Verify the request using the provided hash
        provided_hash = controller.hash
        expected_hash = generate_confirmation_hash(controller.identifier)

        if provided_hash != expected_hash:
            raise cherrypy.HTTPError(400, "Invalid hash")

    @request_property
    def identifier_member(self):
        return app.authentication.identifier_field

    @request_property
    def identifier(self):
        member = self.identifier_member.copy()
        member.name = "user"
        return get_parameter(member, errors = "ignore")

    @request_property
    def hash(self):
        return get_parameter(schema.String("hash"))

    @request_property
    def user(self):
        if self.identifier:
            from cocktail.styled import styled
            print(styled(self.identifier, "slate_blue"))
            return User.get_instance(**{
                self.identifier_member.name: self.identifier
            })

    @field_confirmation("password")
    class ChangePasswordForm(Form):

        model = User

        @request_property
        def source_instance(self):
            return self.controller.user

        def init_data(self, data):
            pass

        @request_property
        def adapter(self):
            adapter = Form.adapter(self)
            adapter.implicit_copy = False
            adapter.copy(
                "password",
                properties = {
                    "member_group": None,
                    "required": True
                }
            )
            adapter.exclude("password_confirmation")
            return adapter

        def after_submit(self):
            app.authentication.set_user_session(self.instance)

    @request_property
    def output(self):
        output = PublishableController.output(self)
        output["identifier"] = self.identifier
        output["hash"] = self.hash
        return output

