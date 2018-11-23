#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Controller
from .dataexport import excluded_members

excluded_members.add(Controller.published_items)

