#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations

for cls_name in ("Configuration", "Website"):
    translations.define(cls_name + ".services.google_analytics",
        ca = u"Google Analytics",
        es = u"Google Analytics",
        en = u"Google Analytics"
    )

    translations.define(cls_name + ".google_analytics_account",
        ca = u"Compte de Google Analytics",
        es = u"Cuenta de Google Analytics",
        en = u"Google Analytics account"
    )

translations.define("Document.ga_tracking_enabled",
    ca = u"Habilitar seguiment amb Google Analytics",
    es = u"Habilitar seguimiento con Google Analytics",
    en = u"Track with Google Analytics"
)

