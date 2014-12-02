#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Template, Slot

Template.add_member(
    Slot("newsletter_header"),
    append = True
)

Template.add_member(
    Slot("newsletter_footer"),
    append = True
)

