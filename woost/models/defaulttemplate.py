#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from .settings import add_setting
from .configuration import Configuration
from .template import Template

translations.load_bundle("woost.models.defaulttemplate")

def with_default_template(template_name, **field_kwargs):

    field_name = "default_%s_template" % template_name

    def decorator(cls):

        # Define the Configuration and Website fields
        add_setting(
            schema.Reference(
                field_name,
                type = Template,
                template_owner = cls,
                custom_translation_key =
                    "woost.models.defaulttemplate.field",
                **field_kwargs
            )
        )

        # Define the method
        base_get_default_template = cls.get_default_template
        cls.get_default_template = lambda self: (
            Configuration.instance.get_setting(field_name)
            or base_get_default_template(self)
        )

        return cls

    return decorator

