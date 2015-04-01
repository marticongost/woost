#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.pkgutils import resolve
from cocktail.translations import get_language
from cocktail.html.autocomplete import Autocomplete as BaseAutocomplete


class Autocomplete(BaseAutocomplete):

    ajax_search = True
    ajax_search_threshold = 100
    show_types = True
    icon_factory = "icon16"

    def _build(self):
        BaseAutocomplete._build(self)
        self.add_resource("/resources/scripts/Autocomplete.js")

    def _ready(self):
        BaseAutocomplete._ready(self)
        self["data-woost-autocomplete-show-types"] = \
            "true" if self.show_types else "false"
        self["data-woost-autocomplete-icon-factory"] = self.icon_factory
        if self.show_types:
            self.add_resource(
                "/cms_metadata?language=%s&format=javascript" % get_language(),
                mime_type = "text/javascript"
            )

    def get_default_ajax_url(self):
        return (
            "/autocomplete/%s/QUERY"
            % self.member.original_member.get_qualified_name(include_ns = True)
        )

    def create_autocomplete_source(self):
        autocomplete_class = resolve(self.member.autocomplete_class)
        return autocomplete_class(self.member)

