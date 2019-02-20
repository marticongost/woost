#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .settings import Settings


class SpecialPagesSection(Settings):
    members = [
        "login_page",
        "generic_error_page",
        "not_found_error_page",
        "forbidden_error_page"
    ]

