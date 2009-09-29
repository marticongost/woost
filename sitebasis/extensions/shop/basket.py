#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
import cherrypy
from sitebasis.extensions.shop.shoporder import ShopOrder
from sitebasis.extensions.shop.shoporderentry import ShopOrderEntry


class Basket(object):

    session_key = "sitebasis.extensions.shop basket"

    @classmethod
    def get(cls):
        """Returns the shop order for the current user session.

        If the user had not started an order yet, a new one is created.
        
        @rtype: L{ShopOrder<sitebasis.extensions.shop.shoporder.ShopOrder>}
        """
        order = getattr(cherrypy.request, "sitebasis_shop_basket", None)

        if order is None:
            order = cls.restore()            
            cherrypy.request.sitebasis_shop_basket = order

        return order
    
    @classmethod
    def drop(cls):
        """Drops the current shop order."""
        cherrypy.session.pop(cls.session_key, None)

    @classmethod
    def store(cls):
        order = cls.get()
        session_data = [(entry.quantity, entry.product.id)
                        for entry in order.entries]
        cherrypy.session[cls.session_key] = session_data

    @classmethod
    def restore(cls):
        session_data = cherrypy.session.get(cls.session_key)
        if session_data is None:
            return None
        else:
            order = ShopOrder()
            order.entries = [
                ShopOrderEntry(
                    quantity = quantity,
                    product = Product.get_instance(product_id)
                )
                for quantity, product_id in session_data
            ]
            return order

