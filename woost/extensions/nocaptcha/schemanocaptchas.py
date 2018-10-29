#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Víctor Manuel Agüero Requena <victor.aguero@whads.com>
"""
import cherrypy
from json import loads
import urllib
import urllib2
from cocktail import schema
from cocktail.html.uigeneration import default_edit_control
from cocktail.schema.exceptions import ValidationError
from woost.models import Configuration


class NoCaptcha(schema.String):
    """A member that handles noCaptcha values."""

    VERIFY_SERVER = "https://www.google.com/recaptcha/api/siteverify"

    def __init__(self, name = None, *args, **kwargs):

        kwargs.setdefault("parameter_name", "g-recaptcha-response")

        if not name:
            name = "nocaptcha"

        schema.String.__init__(self, name, *args, **kwargs)

    def _default_validation(self, context):
        """Validation rule for noCaptcha. Checks that the L{response}
        member is valid for the L{public_key} and L{private_key}
        constraints.
        """
        for error in schema.Member._default_validation(self, context):
            yield error

        value = context.value
        if value:
            params = urllib.urlencode({
                'secret' : Configuration.instance.get_setting('nocaptcha_private_key'),
                'response' : value,
                'remoteip' : cherrypy.request.remote.ip
            })

            request = urllib2.Request(
                url = self.VERIFY_SERVER,
                data = params,
                headers = {
                    "Content-type" : "application/x-www-form-urlencoded",
                    "User-agent" : "Woost noCAPTCHA extension"
                }
            )

            httpresp = urllib2.urlopen(request)
            return_values = httpresp.read()
            httpresp.close()
            response_json = loads(return_values)

            if not response_json['success']:
                yield NoCaptchaValidationError(context)

        else:
            yield NoCaptchaValidationError(context)


class NoCaptchaValidationError(ValidationError):
    """A validation error produced when the user fails a NoCaptcha
    validation.
    """


default_edit_control.set_member_type_display(
    NoCaptcha,
    "woost.extensions.nocaptcha.NoCaptchaBox"
)

