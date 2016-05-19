#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Configuration, LocaleMember

Configuration.add_member(
    LocaleMember(
        "attributes_language",
        member_group = "meta"
    )
)

