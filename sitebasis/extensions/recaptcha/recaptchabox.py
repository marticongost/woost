#-*- coding: utf-8 -*-
u"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
from simplejson import dumps
from cocktail.translations import get_language
from cocktail.html import Element, templates
from sitebasis.extensions.recaptcha import ReCaptchaExtension


class ReCaptchaBox(Element):
    
    API_SSL_SERVER = "https://api-secure.recaptcha.net"
    API_SERVER = "http://api.recaptcha.net"

    tag = None

    def __init__(self, *args, **kwargs):
        Element.__init__(self, *args, **kwargs)
        self.recaptcha_params = {
            "public_key": ReCaptchaExtension.instance.public_key,
            "api_server": self.API_SSL_SERVER if ReCaptchaExtension.instance.ssl 
                          else self.API_SERVER,
            "error_param": "&error=%s" % ("",)
        }
        self.recaptcha_options = {}

    def _ready(self):

        Element._ready(self)

        options = self.recaptcha_options.copy()

        # TODO: There's no Catalan translation available. Add the Catalan
        # translations with the custom_translations option
        language = get_language()
        
        if language == "ca":
            options["lang"] = "es"
        elif language not in ("en", "nl", "fr", "de", "pt", "ru", "es", "tr"):
            options["lang"] = "en"

        options.setdefault("theme", ReCaptchaExtension.instance.theme)

        init_options = Element("script")
        init_options["type"] = "text/javascript"
        init_options.append("var RecaptchaOptions = %s;" % dumps(options))

        init_script = Element()
        init_script.append("""<script type="text/javascript" src="%(api_server)s/challenge?k=%(public_key)s%(error_param)s"></script>

<noscript>
  <iframe src="%(api_server)s/noscript?k=%(public_key)s%(error_param)s" height="300" width="500" frameborder="0"></iframe><br />
  <textarea name="recaptcha_challenge_field" rows="3" cols="40"></textarea>
  <input type='hidden' name='recaptcha_response_field' value='manual_challenge' />
</noscript>
""" % self.recaptcha_params)

        self.append(init_options)
        self.append(init_script)
    
    def _get_value(self):
        return self.textarea.value

    def _set_value(self, value):
        self.textarea.value = value

    value = property(_get_value, _set_value, doc = """
        Gets or sets the content of the rich text editor.
        @type: str
        """)

