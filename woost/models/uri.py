"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.urls import URL

from woost import app
from .publishable import Publishable
from .file import File
from .controller import Controller


class URI(Publishable):

    instantiable = True
    type_group = "resource"
    admin_show_descriptions = False

    members_order = [
        "title",
        "uri",
        "language_specific_uri",
        "image"
    ]

    title = schema.String(
        indexed=True,
        normalized_index=True,
        full_text_indexed=True,
        descriptive=True,
        translated=True,
        spellcheck=True,
        member_group="content"
    )

    uri = schema.String(
        indexed=True,
        member_group="content"
    )

    language_specific_uri = schema.String(
        translated=True,
        member_group="content"
    )

    image = schema.Reference(
        type=File,
        related_end=schema.Collection(),
        relation_constraints={"resource_type": "image"},
        listed_by_default=False,
        member_group="content"
    )

    def get_uri(
        self,
        language=None,
        path=None,
        parameters=None,
        **kwargs
    ):
        url = URL(self.get("language_specific_uri", language) or self.uri)

        if not url.hostname and url.hierarchical:
            url = (
                app.url_mapping.get_url(language=language, **kwargs)
                .merge(url)
            )

        if path or parameters:
            url = url.merge(URL(path=path, query=parameters))

        return url

    def is_internal_content(self, language=None):

        uri = self.get_uri(host="!", language=language)

        if not uri.hostname:
            return True

        resolution = app.url_mapping.resolve(uri)
        return bool(resolution and resolution.website)

