#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from cocktail import schema
from woost.models import Item


class MailingPlatform(Item):

    visible_from_root = False

    members_order = [
        "platform_name",
        "online_version_tag",
        "unsubscription_tag"
    ]

    platform_name = schema.String(
        required = True,
        descriptive = True
    )

    online_version_tag = schema.String(
        edit_control = "cocktail.html.TextArea",
        translated = True
    )

    unsubscription_tag = schema.String(
        edit_control = "cocktail.html.TextArea",
        translated = True
    )

