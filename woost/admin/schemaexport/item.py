#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .schemaexport import excluded_members
from woost.models import Item

excluded_members.add(Item.translations)

