#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
import cherrypy
import hashlib
import smtplib
from email.mime.text import MIMEText
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.translations import translations
from cocktail.modeling import cached_getter
from cocktail.controllers.location import Location
from cocktail.controllers import get_parameter
from cocktail.controllers.formcontrollermixin import FormControllerMixin
from woost.controllers.application import CMS
from woost.controllers.documentcontroller import DocumentController
from woost.controllers.backoffice.usereditnode import PasswordConfirmationError
from woost.extensions.signup import SignUpExtension
from woost.extensions.signup.signuppage import SignUpPage
from woost.models import Item, Site, Language, User

def generate_confirmation_hash(email):
    hash = hashlib.sha1()
    hash.update(email)
    hash.update(SignUpExtension.instance.secret_key)
    return hash.hexdigest()

class SignUpConfirmationController(DocumentController):

    def __init__(self, *args, **kwargs):
        self.email = self.params.read(schema.String("email"))
        self.hash = self.params.read(schema.String("hash"))
    
    view_class = "woost.extensions.signup.SignUpConfirmationView"

    @cached_getter
    def output(self):
        output = DocumentController.output(self)
        # Checking hash code
        if generate_confirmation_hash(self.email) == self.hash:
            instance = User.get_instance(email=self.email)
            if instance:
                # Confirming and enabling user instance
                instance.set("confirmed_email",True)
                instance.set("enabled",True)
                datastore.commit()
                # Autologin after confirmation
                self.context["cms"].authentication.set_user_session(instance)
                output["confirmation_message"] = translations("woost.extensions.signup.SignupSuccessfulConfirmationMessage")
            else:
                output["confirmation_message"] = translations("woost.extensions.signup.SignupFailConfirmationMessage")

        return output

class SignUpController(FormControllerMixin, DocumentController):

    confirm_email = SignUpConfirmationController

    def __init__(self, *args, **kwargs):
        DocumentController.__init__(self, *args, **kwargs)
        FormControllerMixin.__init__(self)

    @cached_getter
    def form_model(self):
        return self.context["publishable"].user_type

    @cached_getter
    def form_adapter(self):

        adapter = FormControllerMixin.form_adapter(self)
        adapter.exclude(
            ["prefered_language",
             "roles",
             "password_confirmation",
             "enabled",
             "confirmed_email"]
            + [key for key in Item.members()]    
        )
        return adapter

    @cached_getter
    def form_schema(self):

        form_schema = FormControllerMixin.form_schema(self)

        # Set schema name in order to keep always the same value
        # although change value of form_model member
        form_schema.name = u"SignUpForm"

        # Adding extra field for password confirmation
        password_confirmation_member = schema.String(
            name = "password_confirmation",
            edit_control = "cocktail.html.PasswordBox",
            required = form_schema.get_member("password")
        )
        form_schema.add_member(password_confirmation_member)

        # Set password_confirmation position just after
        # password member position
        order_list = form_schema.members_order
        pos = order_list.index("password")
        order_list.insert(pos + 1, "password_confirmation")

        # Add validation to compare password_confirmation and
        # password fields
        @form_schema.add_validation
        def validate_password_confirmation(form_schema, value, ctx):
            password = ctx.get_value("password")
            password_confirmation = ctx.get_value("password_confirmation")

            if password and password_confirmation \
            and password != password_confirmation:
                yield PasswordConfirmationError(
                        form_schema, value, ctx)

        return form_schema

    def submit(self):
        FormControllerMixin.submit(self)
        publishable = self.context["publishable"]

        # Adding roles
        instance = self.form_instance
        instance.roles.extend(publishable.roles)

        # If require email confirmation, disabled authenticated access
        # and send email confirmation message
        confirmation_email_template = publishable.confirmation_email_template
        if confirmation_email_template:
            instance.enabled = False
            instance.confirmed_email = False
            confirmation_email_template.send({
                "user": instance,
                "confirmation_url": self.confirmation_url
            })

        # Storing instance
        instance.insert()
        datastore.commit()

    @cached_getter
    def confirmation_url(self): 
        instance = self.form_instance
        location = Location.get_current(relative=False)
        location.path_info = (
            (location.path_info and location.path_info.rstrip("/") or "")
            + "/confirm_email/"
        )
        location.query_string = {
            "email": instance.email,
            "hash": generate_confirmation_hash(instance.email)
        }
        return str(location)
