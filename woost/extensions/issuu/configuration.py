#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail import schema
from woost.models import Configuration
from woost.extensions.issuu.issuuviewersettings import IssuuViewerSettings


Configuration.add_member(
    schema.Collection(
        "issuu_viewer_settings",
        items = schema.Reference(type = IssuuViewerSettings),
        bidirectional = True,
        integral = True,
        related_end = schema.Reference(),
        member_group = "media.issuu"
    )
)

