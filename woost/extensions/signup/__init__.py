#-*- coding: utf-8 -*-
"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""

import random
import string
from cocktail import schema
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail.persistence import datastore
from woost.models import (
    Extension,
    Template,
    EmailTemplate,
    User,
    Controller
)

translations.define("SignUpExtension",
    ca = u"Alta d'usuaris",
    es = u"Alta de usuarios",
    en = u"Sign Up"
)

translations.define("SignUpExtension-plural",
    ca = u"Altas d'usuaris",
    es = u"Altas de usuarios",
    en = u"Signs Up"
)

class SignUpExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet als usuaris registrar-se autònomament en el lloc web""",
            "ca"
        )
        self.set("description",            
            u"""Permite a los usuarios registrarse por si mismos en el sitio""",
            "es"
        )
        self.set("description",
            u"""Allows users to register themselves on the site""",
            "en"
        )
        self.secret_key = self._generate_secret_key()

    def _generate_secret_key(self):
        secret_key = ''
        for i in range(0,8):
            secret_key = secret_key + \
                random.choice(
                    string.letters + string.digits
                )
        return secret_key

    @event_handler
    def handle_loading(cls, event):
        
        from woost.extensions.signup import (
            signuppage,
            signupcontroller,
            strings
        )

        # Extend User model
        if not hasattr(User, "confirmed_email"):
            User.add_member(
                schema.Boolean(
                    "confirmed_email",
                    default = False,
                    Required = True
                )
            )

        # Make sure the sign up template exists
        signup_view = Template.get_instance(
            qname = u"woost.extensions.signup.signup_template"
        )

        if signup_view is None:
            signup_view = Template()
            signup_view.identifier = u"woost.extensions.signup.SignUpView"
            signup_view.engine = u"cocktail"
            signup_view.qname = u"woost.extensions.signup.signup_template"
            signup_view.set("title", "Sign up view", "en")
            signup_view.set("title", "Vista de alta de usuarios", "es")
            signup_view.set("title", "Vista d'alta d'usuaris", "ca")
            signup_view.insert()

        # Make sure the sign up controller exists
        signup_controller = Controller.get_instance(
            qname = u"woost.extensions.signup.signup_controller"
        )
        
        if signup_controller is None:
            signup_controller = Controller()
            signup_controller.python_name = u"woost.extensions.signup.signupcontroller.SignUpController"
            signup_controller.qname = u"woost.extensions.signup.signup_controller"
            signup_controller.set("title", "Sign Up controller", "en")
            signup_controller.set("title", "Controlador de alta de usuarios", "es")
            signup_controller.set("title", "Controlador d'alta d'usuaris", "ca")
            signup_controller.insert()

        # Make sure the confirmation email template exists
        confirmation_email_template = EmailTemplate.get_instance(
            qname = u"woost.extensions.signup.signup_confirmation_email_template"
        )
        
        if confirmation_email_template is None:
            confirmation_email_template = EmailTemplate()
            confirmation_email_template.python_name = u"woost.extensions.signup.signupconfirmationemailtemplate.SignUpConfirmationEmailTemplate"
            confirmation_email_template.qname = u"woost.extensions.signup.signup_confirmation_email_template"
            # title
            confirmation_email_template.set("title", u"Sign Up Confirmation email template ", "en")
            confirmation_email_template.set("title", u"Plantilla de email de confirmación de alta de usuario", "es")
            confirmation_email_template.set("title", u"Plantilla de correu electrònic de confirmació d'alta d'usuari", "ca")
            # subject
            confirmation_email_template.set("subject", u"User account confirmation", "en")
            confirmation_email_template.set("subject", u"Confirmación de cuenta de usuario", "es")
            confirmation_email_template.set("subject", u"Confirmació de compte d'usuari", "ca")
            # template engine
            confirmation_email_template.template_engine = u"mako"
            # body
            confirmation_email_template.set("body", u"""
                Hello ${user.email}. Click here to confirm your email account.
                <br/> <a href='${confirmation_url}'>${confirmation_url}</a>
            """, "en")
            confirmation_email_template.set("body", u"""
                Hola ${user.email}. Has clic para confirmar tu cuenta de usuario.
                <br/> <a href='${confirmation_url}'>${confirmation_url}</a>
            """, "es")
            confirmation_email_template.set("body", u"""
                Hola ${user.email}. Fes clic per confirmar el teu compte d'usuari.
                <br/> <a href='${confirmation_url}'>${confirmation_url}</a>
            """, "ca")
            # sender
            confirmation_email_template.set("sender", u"'no-reply@woost.info'")
            # receivers
            confirmation_email_template.set("receivers", u"[user.email]")

            confirmation_email_template.insert()

        datastore.commit()

