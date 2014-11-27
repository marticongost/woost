#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from decimal import Decimal
from cocktail.translations import translations
from cocktail import schema
from cocktail.html.datadisplay import display_factory


class NewsletterContentLayout(schema.String):

    layouts = ["image_top", "image_left", "image_right"]

    def __init__(self, *args, **kwargs):

        kwargs.setdefault("searchable", False)
        kwargs.setdefault("text_search", False)
        
        if "edit_control" not in kwargs:
            kwargs.setdefault("edit_control",
                display_factory(
                    "cocktail.html.RadioSelector",
                    empty_option_displayed = True
                )
            )

        if "enumeration" not in kwargs:
            kwargs["enumeration"] = lambda ctx: self.layouts

        schema.String.__init__(self, *args, **kwargs)

    def translate_value(self, value, language = None, **kwargs):
        return translations(
            "woost.extensions.newsletters.NewsletterContentLayout=" + value
                if value
                else "woost.extensions.newsletters.inherited_value",
            language = language,
            **kwargs
        )


class NewsletterContentImageSize(schema.String):

    sizes = ["original", "one_third", "one_half"]

    def __init__(self, *args, **kwargs):

        kwargs.setdefault("searchable", False)
        kwargs.setdefault("text_search", False)

        if "edit_control" not in kwargs:
            kwargs.setdefault("edit_control",
                display_factory(
                    "cocktail.html.RadioSelector",
                    empty_option_displayed = True
                )
            )

        if "enumeration" not in kwargs:
            kwargs["enumeration"] = lambda ctx: self.sizes

        schema.String.__init__(self, *args, **kwargs)

    def translate_value(self, value, language = None, **kwargs):
        return translations(
            "woost.extensions.newsletters.NewsletterContentImageSize=" + value
                if value
                else "woost.extensions.newsletters.inherited_value",
            language = language,
            **kwargs
        )


class NewsletterContentAppearence(schema.String):

    appearences = [
        "woost.extensions.newsletters.NewsletterContentView"
    ]

    def __init__(self, *args, **kwargs):

        kwargs.setdefault("searchable", False)
        kwargs.setdefault("text_search", False)

        if "edit_control" not in kwargs:
            kwargs.setdefault("edit_control",
                display_factory(
                    "cocktail.html.RadioSelector",
                    empty_option_displayed = True
                )
            )

        if "enumeration" not in kwargs:
            kwargs["enumeration"] = lambda ctx: self.appearences

        schema.String.__init__(self, *args, **kwargs)

    def translate_value(self, value, language = None, **kwargs):
        return translations(
            "woost.extensions.newsletters.NewsletterContentAppearence=" + value
                if value
                else "woost.extensions.newsletters.inherited_value",
            language = language,
            **kwargs
        )


class Spacing(schema.Decimal):

    factors = [
        Decimal("0"),
        Decimal("0.5"),
        Decimal("1"),
        Decimal("1.5"),
        Decimal("2"),
        Decimal("3")
    ]

    def __init__(self, *args, **kwargs):

        if "enumeration" not in kwargs:
            kwargs["enumeration"] = lambda ctx: self.factors

        kwargs.setdefault("edit_control", "cocktail.html.DropdownSelector")
        schema.Decimal.__init__(self, *args, **kwargs)

