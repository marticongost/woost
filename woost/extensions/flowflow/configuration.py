#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.translations import translations
from woost.models import Configuration

translations.load_bundle("woost.extensions.flowflow.configuration")


Configuration.add_member(
    schema.URL(
        "flow_flow_url",
        required = True,
        default = "https://flowflow.whads.com",
        member_group = "services"
    ),
    append = True
)

