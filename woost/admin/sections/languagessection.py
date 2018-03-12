#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .settings import Settings


class LanguagesSection(Settings):
    members = [
        "languages",
        "published_languages",
        "virtual_languages",
        "default_language",
        "fallback_languages",
        "heed_client_language",
        "backoffice_language",
        "backoffice_language_chain"
    ]

