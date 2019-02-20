#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .settings import Settings


class SystemSection(Settings):
    members = [
        "timezone",
        "smtp_host",
        "smtp_user",
        "smtp_password"
    ]

