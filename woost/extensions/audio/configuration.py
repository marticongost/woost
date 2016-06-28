#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models import Configuration
from woost.extensions.audio.audiodecoder import AudioDecoder
from woost.extensions.audio.audioencoder import AudioEncoder

translations.load_bundle("woost.extensions.audio.configuration")

pos = Configuration.groups_order.index("presentation.images")
Configuration.groups_order.insert(pos + 1, "audio")
Configuration.members_order += ["audio_decoders", "audio_encoders"]

Configuration.add_member(
    schema.Collection("audio_decoders",
        items = schema.Reference(type = AudioDecoder),
        related_end = schema.Reference(),
        integral = True,
        member_group = "presentation.audio"
    )
)

Configuration.add_member(
    schema.Collection("audio_encoders",
        items = schema.Reference(type = AudioEncoder),
        related_end = schema.Reference(),
        integral = True,
        member_group = "presentation.audio"
    )
)

