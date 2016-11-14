#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from cocktail.persistence import MigrationStep

step = MigrationStep("woost.extensions.sitemap: set defaults to None")

@when(step.executing)
def set_sitemap_defaults_to_none(e):

    from decimal import Decimal
    from woost.models import Publishable

    default_priority = Decimal("0.5")

    for publishable in Publishable.select():
        if publishable.sitemap_priority == default_priority:
            publishable.sitemap_priority = None

