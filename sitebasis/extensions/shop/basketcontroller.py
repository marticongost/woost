#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
import cherrypy
from cocktail import schema
from cocktail.controllers import get_parameter
from sitebasis.extensions.shop.shopcontroller import ShopController
from sitebasis.extensions.shop.basket import Basket


class ShopController(ShopController):

    @cherrypy.expose
    def update(self):
        
        product = get_parameter(schema.Reference("product", type = Product))
        quantity = get_parameter(schema.Integer("quantity", min = 0))

        if product is not None and quantity is not None:
            shop_order = Basket.get()
            shop_order.set_product_quantity(product, quantity)
            Basket.store()

        self.parent_redirect()

    def parent_redirect(self):
        parts = cherrypy.request.path_info.strip("/").split("/")
        parts.pop(-1)
        path = "/" + "/".join(parts)
        raise cherrypy.HTTPRedirect(path)

