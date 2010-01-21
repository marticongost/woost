#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from cocktail.modeling import cached_getter
from woost.controllers import PageHandler
from woost.extensions.shop.basket import Basket


class ShopController(PageHandler):

    @cached_getter
    def output(self):
        output = PageHandler.output(self)
        output["shop_order"] = Basket.get()
        return output

