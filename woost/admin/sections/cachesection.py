#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .settings import Settings


class CacheSection(Settings):
    members = [
        "caching_policies"
    ]
