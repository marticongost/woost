#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from urllib import urlopen, urlencode
from simplejson import dumps
from cocktail.translations import (
    get_language,
    translations
)
from cocktail import schema
from cocktail.html.datadisplay import display_factory
from woost.models import Item, Language
from woost.extensions.opengraph import OpenGraphExtension

facebook_locales = {
    "Catalan": "1",
    "Czech": "2",
    "Welsh": "3",
    "Danish": "4",
    "German": "5",
    "English (Upside Down)": "51",
    "English (US)": "6",
    "Spanish": "23",
    "Spanish (Spain)": "7",
    "Finnish": "8",
    "French (France)": "9",
    "Hungarian": "30",
    "Italian": "10",
    "Japanese": "11",
    "Korean": "12",
    "Norwegian (bokmal)": "13",
    "Dutch": "14",
    "Polish": "15",
    "Portuguese (Brazil)": "16",
    "Portuguese (Portugal)": "31",
    "Romanian": "32",
    "Russian": "17",
    "Slovak": "33",
    "Slovenian": "34",
    "Swedish": "18",
    "Thai": "35",
    "Turkish": "19",
    "Simplified Chinese (China)": "20",
    "Traditional Chinese (Hong Kong)": "21",
    "Traditional Chinese (Taiwan)": "22",
    "Afrikaans": "36",
    "Bengali": "45",
    "Bulgarian": "37",
    "Croatian": "38",
    "English (UK)": "24",
    "French (Canada)": "44",
    "Greek": "39",
    "Hindi": "46",
    "Indonesian": "25",
    "Lithuanian": "40",
    "Malay": "41",
    "Punjabi": "47",
    "Serbian": "42",
    "Filipino": "26",
    "Tamil": "48",
    "Telugu": "49",
    "Malayalam": "50",
    "Vietnamese": "27",
    "Arabic": "28",
    "Hebrew": "29"    
}


class FacebookPublicationTarget(Item):

    members_order = [
        "title",
        "graph_object_id",
        "administrator_id",
        "app_id",
        "app_secret",
        "auth_token",
        "languages",
        "targeting"
    ]

    visible_from_root = False

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        descriptive = True,
        listed_by_default = False
    )

    graph_object_id = schema.String(
        required = True
    )

    administrator_id = schema.String(
        listed_by_default = False        
    )

    app_id = schema.String(
        required = True,
        listed_by_default = False
    )

    app_secret = schema.String(
        required = True,
        listed_by_default = False,
        text_search = False
    )

    auth_token = schema.String(
        editable = False,
        text_search = False,
        translate_value = lambda value, language = None, **kwargs:
            translations(
                "FacebookPublicationTarget.auth_token-%s"
                % ("conceded" if value else "pending"),
                language,
                **kwargs
            )
    )

    languages = schema.Collection(
        items = schema.String(
            enumeration = lambda ctx: Language.codes,
            translate_value = lambda value, language = None, **kwargs:
                "" if not value else translations(value)
        )
    )

    targeting = schema.String(
        edit_control = display_factory(
            "cocktail.html.CodeEditor",
            syntax = "python",
            cols = 80
        ),
        text_search = False,
        listed_by_default = False
    )

    def publish(self, publishable):

        if self.auth_token is None:
            raise ValueError(
                "Can't publish %s to %s: missing authorization token."
                % (publishable, self)
            )

        graph_url = "https://graph.facebook.com/%s/feed" % self.graph_object_id                
        post_data = self._get_publication_parameters(publishable)        
        encoded_post_data = dict(
            (k, v.encode("utf-8") if isinstance(v, unicode) else v)
            for k, v in post_data.iteritems()
        )
        response = urlopen(graph_url, urlencode(encoded_post_data))
        status = response.getcode()
        if status < 200 or status > 299:
            raise FacebookPublicationError(response.read())

    def _get_publication_parameters(self, publishable):

        og = OpenGraphExtension.instance
        og_properties = og.get_properties(publishable)
        
        post_data = {
            "access_token": self.auth_token,
            "name": og_properties.get("og:title") or translations(publishable),
            "link": og_properties.get("og:url")
        }

        # Disregard any default image; only show an image if the published
        # content defines one
        if "og:image" not in og_properties:
            post_data["picture"] = ""

        if self.targeting:
            context = {
                "language": get_language(),
                "og_properties": og_properties,
                "publishable": publishable,
                "locales": facebook_locales,
                "include_locales": (
                    lambda included: ",".join(
                        facebook_locales[loc_name] for loc_name in included
                    )
                ),
                "exclude_locales": (
                    lambda excluded: ",".join(
                        loc_id 
                        for loc_name, loc_id in facebook_locales.iteritems()
                        if loc_name not in excluded
                    )
                )
            }
            targeting_code = self.targeting.replace("\r\n", "\n")
            exec targeting_code in context
            targeting = context.get("targeting")
            if targeting:
                post_data["targeting"] = dumps(targeting)

        return post_data


class FacebookPublicationError(Exception):

    def __init__(self, response):
        Exception.__init__(self, response)
        self.response = response

