"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.stringutils import normalize
from cocktail.translations import translate_locale
from cocktail import schema


class LocaleMember(schema.String):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("search_control", "cocktail.html.DropdownSelector")
        kwargs.setdefault("enumeration", _locales_enumeration)
        schema.String.__init__(self, *args, **kwargs)

    def translate_value(self, value, language=None, **kwargs):
        if not value:
            return schema.String.translate_value(
                self,
                value,
                language=language,
                **kwargs
            )
        else:
            return translate_locale(value, language=language)

def _locales_enumeration(ctx):
    from woost.models.configuration import Configuration
    return sorted(
        Configuration.instance.languages,
        key=lambda locale: normalize(translate_locale(locale))
    )

