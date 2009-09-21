#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail.events import event_handler
from cocktail.translations import translations
from sitebasis.models import Extension

translations.define("ShopExtension",
    ca = u"Botiga",
    es = u"Tienda",
    en = u"Shop"
)

translations.define("ShopExtension-plural",
    ca = u"Botigues",
    es = u"Tiendas",
    en = u"Shops"
)


class ShopExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Proporciona els elements necessaris per implementar una botiga
            electrònica.""",
            "ca"
        )
        self.set("description",            
            u"""Proporciona los elementos necesarios para implementar una
            tienda electrónica.""",
            "es"
        )
        self.set("description",
            u"""Supplies the building blocks required to implement an online
            shop.""",
            "en"
        )

    @event_handler
    def handle_loading(cls, event):
        
        from sitebasis.extensions.shop import (
            strings,
            product,
            productcategory,
            shoporder,
            shoporderentry,
            shippingaddress,
            customer
        )

