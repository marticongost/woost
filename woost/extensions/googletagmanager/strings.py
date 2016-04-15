#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations

# Configuration / Website
#------------------------------------------------------------------------------
for cls_name in ("Configuration", "Website"):
    translations.define(cls_name + ".services.google_tag_manager",
        ca = u"Google Tag Manager",
        es = u"Google Tag Manager",
        en = u"Google Tag Manager"
    )

    translations.define(cls_name + ".google_tag_manager_account",
        ca = u"Compte de Google Tag Manager",
        es = u"Cuenta de Google Tag Manager",
        en = u"Google Tag Manager account"
    )

