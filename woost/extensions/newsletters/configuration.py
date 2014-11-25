#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from cocktail import schema
from woost.models import Configuration
from woost.extensions.newsletters.mailingplatform import MailingPlatform

Configuration.add_member(
    schema.Collection("mailing_platforms",
        items = schema.Reference(type = MailingPlatform),
        member_group = "services.mailing_platform",
        related_end = schema.Reference(),
        integral = True
    )
)
