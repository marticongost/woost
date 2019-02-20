#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.pkgutils import resolve
from cocktail.translations import require_language
from cocktail.html.resources import resource_repositories
from cocktail.html.autocomplete import Autocomplete as BaseAutocomplete
from woost import app


class Autocomplete(BaseAutocomplete):

    ajax_search = True
    ajax_search_threshold = 100
    show_icons = True
    show_types = True
    icon_factory = "icon16"

    def _build(self):
        BaseAutocomplete._build(self)
        self.add_resource("woost://scripts/autocomplete.js")

    def _ready(self):

        BaseAutocomplete._ready(self)

        self["data-woost-autocomplete-show-types"] = \
            "true" if self.show_types else "false"
        self["data-woost-autocomplete-show-icons"] = \
            "true" if self.show_icons else "false"
        self["data-woost-autocomplete-icon-factory"] = self.icon_factory

        self.set_client_param(
            "emptyIcon",
            resource_repositories.normalize_uri("woost://images/empty_set.png")
        )

        if self.show_types:
            self.add_resource(
                app.url_mapping.get_url(
                    path = ["cms_metadata"],
                    parameters = {
                        "language": require_language(),
                        "format": "javascript"
                    }
                ),
                mime_type = "text/javascript"
            )

    def get_default_ajax_url(self):
        return app.url_mapping.get_url(
            path = [
                "autocomplete",
                self.member.original_member.get_qualified_name(
                    include_ns = True
                ),
                "QUERY"
            ],
            parameterers = {"lang": require_language()}
        )

    def create_autocomplete_source(self):
        autocomplete_class = resolve(self.member.autocomplete_class)
        return autocomplete_class(self.member)

