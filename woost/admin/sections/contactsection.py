#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from .settings import Settings


class ContactSection(Settings):
    members = [
        "organization_name",
        "organization_url",
        "address",
        "town",
        "region",
        "postal_code",
        "country",
        "phone_number",
        "fax_number",
        "email",
        "technical_contact_email"
    ]

