#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.pkgutils import import_object
from woost.models import (
    Publishable,
    Controller,
    AccessLevel,
    LocaleMember
)


class Admin(Publishable):

    members_order = [
        "title",
        "default_language",
        "root_section",
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

    root_section = schema.String(
        required = True,
        default = "woost.admin.sections.rootsection.RootSection"
    )

    ui_components = schema.Collection(
        items = schema.String()
    )

    def create_root_section(self):
        section_class = import_object(self.root_section)
        return section_class(None)

