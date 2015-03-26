#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import User, Role

def _translators_enumeration(ctx):
    translators_role = Role.get_instance(
        qname = "woost.extensions.translationworkflow.roles.translators"
    )
    if translators_role is not None:
        return translators_role.users

assign_translator_schema = schema.Schema(
    "woost.extensions.translationworkflow.assign_translator_schema",
    members = [
        schema.Reference("translator",
            type = User,
            required = True,
            enumeration = _translators_enumeration
        )
    ]
)

