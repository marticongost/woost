#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from cocktail.controllers.csrfprotection import (
    CSRFProtection,
    CSRFProtectionExemption
)
from woost import app
from woost.models import ModifyPermission
from .newsletter import Newsletter


@when(CSRFProtection.deciding_injection)
def exempt_newsletters(e):
    if (
        isinstance(app.publishable, Newsletter)
        and not app.user.has_permission(
            ModifyPermission,
            target = app.publishable
        )
    ):
        raise CSRFProtectionExemption()

