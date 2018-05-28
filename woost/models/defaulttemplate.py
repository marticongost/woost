#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from .configuration import Configuration
from .website import Website
from .template import Template

translations.load_bundle("woost.models.defaulttemplate")

def with_default_template(template_name, **field_kwargs):

    field_name = "default_%s_template" % template_name

    def decorator(cls):

        # Define the Configuration and Website fields
        for config_class in (Configuration, Website):
            config_class.add_member(
                schema.Reference(
                    field_name,
                    type = Template,
                    related_end = schema.Reference(),
                    template_owner = cls,
                    member_group = "presentation.appearence",
                    custom_translation_key =
                        "woost.models.defaulttemplate.field",
                    **field_kwargs
                ),
                append = True
            )

        # Define the method
        base_get_default_template = cls.get_default_template
        cls.get_default_template = lambda self: (
            Configuration.instance.get_setting(field_name)
            or base_get_default_template(self)
        )
        return cls

    return decorator

