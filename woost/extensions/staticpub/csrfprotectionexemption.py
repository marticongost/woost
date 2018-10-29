#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from cocktail.controllers.csrfprotection import (
    CSRFProtection,
    CSRFProtectionExemption
)
from woost.extensions.staticpub import generating_static_site

@when(CSRFProtection.deciding_injection)
def disable_csrf_protection_in_static_pages(e):
    if generating_static_site():
        raise CSRFProtectionExemption()

