#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .settings import Settings


class MetaSection(Settings):
    members = [
        "site_name",
        "hosts",
        "logo",
        "icons",
        "keywords",
        "description",
        "meta_tags",
        "robots_should_index"
    ]

