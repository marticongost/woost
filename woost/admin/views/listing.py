#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Item
from .views import View, register_view

listing = View("listing")
register_view(listing, Item)

