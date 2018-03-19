#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models import add_setting, Configuration
from woost.extensions.audio.audiodecoder import AudioDecoder
from woost.extensions.audio.audioencoder import AudioEncoder

translations.load_bundle("woost.extensions.audio.configuration")

add_setting(
    schema.Collection(
        "audio_decoders",
        items = schema.Reference(type = AudioDecoder),
        bidirectional = True,
        integral = True
    ),
    scopes = [Configuration]
)

add_setting(
    schema.Collection(
        "audio_encoders",
        items = schema.Reference(type = AudioEncoder),
        bidirectional = True,
        integral = True
    ),
    scopes = [Configuration]
)

