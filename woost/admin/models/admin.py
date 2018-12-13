#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from threading import Lock
from cocktail import schema
from cocktail.pkgutils import import_object
from woost.models import (
    Publishable,
    Controller,
    AccessLevel,
    LocaleMember
)

_root_sections = {}
_root_sections_lock = Lock()


class Admin(Publishable):

    members_order = [
        "title",
        "default_language",
        "root_section",
        "main_ui_component",
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

    main_ui_component = schema.String(
        required = True,
        default = "woost.admin.ui.Layout"
    )

    ui_components = schema.Collection(
        items = schema.String()
    )

    def create_root_section(self):
        section_cls = import_object(self.root_section)
        return section_cls(None)

    def get_root_section(self):
        key = (self.root_section, self.id)
        try:
            return _root_sections[key]
        except KeyError:
            with _root_sections_lock:
                try:
                    return _root_sections[key]
                except KeyError:
                    root = self.create_root_section()
                    _root_sections[key] = root
                    return root

