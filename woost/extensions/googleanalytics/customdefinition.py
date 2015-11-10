#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Item, Publishable, Website, get_current_website
from .utils import get_ga_value


class GoogleAnalyticsCustomDefinition(Item):

    visible_from_root = False

    members_order = [
        "title",
        "definition_type",
        "enabled",
        "content_types",
        "websites",
        "initialization"
    ]

    title = schema.String(
        required = True,
        indexed = True,
        unique = True,
        translated = True,
        descriptive = True
    )

    definition_type = schema.String(
        required = True,
        default = "dimension",
        enumeration = ["dimension", "metric"]
    )

    enabled = schema.Boolean(
        required = True,
        default = True
    )

    content_types = schema.Collection(
        items = schema.Reference(class_family = Item),
        default = [Publishable],
        min = 1
    )

    websites = schema.Collection(
        items = schema.Reference(type = Website),
        related_end = schema.Collection(),
        edit_control = "cocktail.html.CheckList"
    )

    initialization = schema.CodeBlock(
        required = True,
        language = "python"
    )

    def applies(self, publishable, website = None):

        if not isinstance(publishable, tuple(self.content_types)):
            return False

        websites = self.websites
        if websites:
            if website is None:
                website = get_current_website()
            if website not in websites:
                return False

        return True

    def apply(self, publishable, values, index = None, env = None):

        if index is None:
            from woost.models import Configuration
            defs = Configuration.instance.google_analytics_custom_definitions
            index = defs.index(self)

        context = {
            "publishable": publishable,
            "index": index,
            "value": schema.undefined,
            "undefined": schema.undefined,
            "env": {} if env is None else env
        }

        GoogleAnalyticsCustomDefinition.initialization.execute(self, context)
        index = context["index"]
        if index is not None:
            value = context["value"]
            if value is not schema.undefined:
                key = self.definition_type + str(index)
                value = get_ga_value(value)
                values[key] = value

