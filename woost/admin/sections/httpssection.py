#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .settings import Settings


class HTTPSSection(Settings):
    members = [
        "https_policy",
        "https_persistence"
    ]

