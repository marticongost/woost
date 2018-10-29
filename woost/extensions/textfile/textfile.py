#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Publishable, with_default_controller


@with_default_controller("text_file")
class TextFile(Publishable):

    instantiable = True
    per_language_publication = False
    default_mime_type = "text/plain"
    default_hidden = True

    members_order = ["title", "content"]

    title = schema.String(
        translated = True,
        descriptive = True,
        spellcheck = True,
        listed_by_default = False,
        member_group = "content"
    )

    content = schema.String(
        edit_control = "cocktail.html.TextArea",
        listed_by_default = False,
        member_group = "content"
    )

