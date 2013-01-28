#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Event
from woost.extensions.blocks.slot import Slot

# Replace the Event.body text member with a list of blocks
Event.body.visible = False

Event.add_member(Slot("blocks"))

