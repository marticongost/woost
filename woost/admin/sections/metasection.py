#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .settings import Settings


class MetaSection(Settings):
    members = [
        "site_name",
        "hosts",
        "logo",
        "icon",
        "keywords",
        "description",
        "meta_tags",
        "robots_should_index"
    ]

