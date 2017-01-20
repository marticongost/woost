#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Víctor Manuel Agüero Requena <victor.aguero@whads.com>
"""
from cocktail.translations import translations

# Configuration / Website
#------------------------------------------------------------------------------
for cls_name in ("Configuration", "Website"):
    translations.define(cls_name + ".services.nocaptcha",
        ca = u"Google NoCaptcha",
        es = u"Google NoCaptcha",
        en = u"Google NoCaptcha"
    )

    translations.define(cls_name + ".nocaptcha_public_key",
        ca = u"Clau pública",
        es = u"Clave pública",
        en = u"Public key"
    )

    translations.define(cls_name + ".nocaptcha_private_key",
        ca = u"Clau privada",
        es = u"Clave pública",
        en = u"Private key"
    )

translations.define("woost.extensions.nocaptcha.schemanocaptchas.NoCaptchaValidationError-instance",
    ca = u"Ho sentim, el CAPTCHA és erroni. Si us plau, intenti-ho de nou.",
    es = u"Lo sentimos, el CAPTCHA es erroneo. Por favor inténtelo de nuevo.",
    en = u"Sorry, you failed the CAPTCHA. Please try again."
)

