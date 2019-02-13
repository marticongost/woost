#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Item
from .views import View, register_view


class Listing(View):
    pass

listing = Listing("listing")
register_view(listing, Item)

