#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Javier Marrero <javier.marrero@whads.com>
"""
from decimal import Decimal
from cocktail.translations import translations
from cocktail import schema
from cocktail.html.datadisplay import display_factory
from woost.models import Configuration
from woost.models.rendering import ImageFactory


class NewsletterContentLayout(schema.String):

    enumeration = ["image_top", "image_left", "image_right"]

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
            kwargs["enumeration"] = lambda ctx: self.__class__.enumeration

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

    enumeration = ["original", "one_third", "one_half"]

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
            kwargs["enumeration"] = lambda ctx: self.__class__.enumeration

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

    enumeration = [
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
            kwargs["enumeration"] = lambda ctx: self.__class__.enumeration

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

    enumeration = [
        Decimal("0"),
        Decimal("0.5"),
        Decimal("1"),
        Decimal("1.5"),
        Decimal("2"),
        Decimal("3")
    ]

    def __init__(self, *args, **kwargs):

        if "enumeration" not in kwargs:
            kwargs["enumeration"] = lambda ctx: self.__class__.enumeration

        kwargs.setdefault("edit_control", "cocktail.html.DropdownSelector")
        schema.Decimal.__init__(self, *args, **kwargs)

    def translate_value(self, value, language = None, **kwargs):
        if value is None and not self.required:
            return translations(
                "woost.extensions.newsletters.inherited_value",
                language = language,
                **kwargs
            )
        else:
            return schema.Decimal.translate_value(
                self,
                value,
                language = language,
                **kwargs
            )


class LinkStyle(schema.String):

    enumeration = ["minimal", "linked_text", "explicit_link"]

    def __init__(self, *args, **kwargs):
        
        if "enumeration" not in kwargs:
            kwargs["enumeration"] = lambda ctx: self.__class__.enumeration
        
        if "edit_control" not in kwargs:
            kwargs["edit_control"] = display_factory(
                "cocktail.html.RadioSelector",
                empty_option_displayed = True
            )

        schema.String.__init__(self, *args, **kwargs)

    def translate_value(self, value, language = None, **kwargs):
        return translations(
            "woost.extensions.newsletters.LinkStyle=" + value
                if value
                else "woost.extensions.newsletters.inherited_value",
            language = language,
            **kwargs
        )


class BorderStyle(schema.String):

    enumeration = []

    def __init__(self, *args, **kwargs):

        if "enumeration" not in kwargs:
            kwargs["enumeration"] = lambda ctx: self.__class__.enumeration

        if "edit_control" not in kwargs:
            kwargs["edit_control"] = display_factory(
                "cocktail.html.RadioSelector",
                empty_option_displayed = True
            )

        schema.String.__init__(self, *args, **kwargs)

    def translate_value(self, value, language = None, **kwargs):
        return translations(
            "woost.extensions.newsletters.BorderStyle=" + (value or "None"),
            language = language,
            **kwargs
        )


class HeadingPosition(schema.String):

    enumeration = ["top", "inside"]

    def __init__(self, *args, **kwargs):
        
        if "enumeration" not in kwargs:
            kwargs["enumeration"] = lambda ctx: self.__class__.enumeration
        
        if "edit_control" not in kwargs:
            kwargs["edit_control"] = display_factory(
                "cocktail.html.RadioSelector",
                empty_option_displayed = True
            )

        schema.String.__init__(self, *args, **kwargs)

    def translate_value(self, value, language = None, **kwargs):
        return translations(
            "woost.extensions.newsletters.HeadingPosition=" + value
                if value
                else "woost.extensions.newsletters.inherited_value",
            language = language,
            **kwargs
        )


def _iter_newsletter_image_factories():
    for factory in Configuration.instance.image_factories:
        if factory.applicable_to_newsletters:
            yield factory

def _newsletter_image_factories_enum(ctx):
    return list(_iter_newsletter_image_factories())


class NewsletterImageFactory(schema.Reference):

    def __init__(self, *args, **kwargs):
        
        kwargs.setdefault("type", ImageFactory)
        kwargs.setdefault("enumeration", _newsletter_image_factories_enum)
        kwargs.setdefault("edit_control", "cocktail.html.DropdownSelector")

        if "bidirectional" not in kwargs and "related_end" not in kwargs:
            kwargs["related_end"] = schema.Collection()
        
        schema.Reference.__init__(self, *args, **kwargs)

    def translate_value(self, value, language = None, **kwargs):

        if value is None:
            return translations(
                "woost.extensions.newsletters.inherited_value",
                language = language,
                **kwargs
            )

        return schema.Reference.translate_value(
            self,
            value,
            language = language,
            **kwargs
        )

