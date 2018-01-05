#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import (
    Publishable,
    Controller,
    AccessLevel,
    LocaleMember
)
from .section import Section


class Admin(Publishable):

    members_order = [
        "title",
        "default_language",
        "sections",
        "ui_components"
    ]

    default_access_level = schema.DynamicDefault(lambda:
        AccessLevel.get_instance(qname = "woost.editor_access_level")
    )

    default_controller = schema.DynamicDefault(lambda:
        AccessLevel.get_instance(qname = "woost.admin.admin_controller")
    )

    title = schema.String(
        required = True,
        descriptive = True,
        translated = True
    )

    default_language = LocaleMember(
        required = True
    )

    sections = schema.Collection(
        items = schema.Reference(type = Section),
        related_end = schema.Collection(),
        integral = True
    )

    ui_components = schema.Collection(
        items = schema.String()
    )

