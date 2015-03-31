#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models import User, LocaleMember
from .path import TranslationWorkflowPath

User.add_member(
    schema.Collection("translation_proficiencies",
        items = TranslationWorkflowPath
    )
)

