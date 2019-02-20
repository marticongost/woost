#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Publishable, Document
from .crud import CRUD


class PublishableItemsSection(CRUD):
    model = Publishable
    views = ["site_tree", "listing"]

