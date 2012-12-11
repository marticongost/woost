#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Site
from woost.extensions.audio.audiodecoder import AudioDecoder
from woost.extensions.audio.audioencoder import AudioEncoder

pos = Site.groups_order.index("rendering")
Site.groups_order.insert(pos + 1, "audio")
Site.members_order += ["audio_decoders", "audio_encoders"]

Site.add_member(
    schema.Collection("audio_decoders",
        items = schema.Reference(type = AudioDecoder),
        related_end = schema.Reference(),
        integral = True,
        member_group = "audio"
    )
)

Site.add_member(
    schema.Collection("audio_encoders",
        items = schema.Reference(type = AudioEncoder),
        related_end = schema.Reference(),
        integral = True,
        member_group = "audio"
    )
)

