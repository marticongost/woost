#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from .settings import add_setting
from .configuration import Configuration
from .controller import Controller

translations.load_bundle("woost.models.defaultcontroller")

def get_default_controllers():
    return [
        member
        for member in Configuration.iter_members()
        if isinstance(member, schema.Reference)
        and member.related_type
        and issubclass(member.related_type, Controller)
        and getattr(member, "controller_owner", None)
    ]

def with_default_controller(controller_name, **field_kwargs):

    field_name = "default_%s_controller" % controller_name

    def decorator(cls):

        # Define the Configuration and Website fields
        add_setting(
            schema.Reference(
                field_name,
                type = Controller,
                controller_owner = cls,
                custom_translation_key =
                    "woost.models.defaultcontroller.field",
                **field_kwargs
            )
        )

        # Define the method
        base_get_default_controller = cls.get_default_controller
        cls.get_default_controller = lambda self: (
            Configuration.instance.get_setting(field_name)
            or base_get_default_controller(self)
        )
        return cls

    return decorator

