#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
import cherrypy
from cocktail.persistence import datastore
from sitebasis.extensions.shop.shoporder import ShopOrder
from sitebasis.extensions.shop.shoporderentry import ShopOrderEntry
from sitebasis.extensions.shop.product import Product


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

            if order is None:
                order = ShopOrder()

            cherrypy.request.sitebasis_shop_basket = order

        return order
    
    @classmethod
    def drop(cls):
        """Drops the current shop order."""
        cherrypy.session.pop(cls.session_key, None)

    @classmethod
    def store(cls):
        order = cls.get()
        order.insert()
        datastore.commit()
        cherrypy.session[cls.session_key] = order.id

    @classmethod
    def restore(cls):
        session_data = cherrypy.session.get(cls.session_key)

        if session_data is None:
            return None
        else:
            return ShopOrder.get_instance(session_data)

