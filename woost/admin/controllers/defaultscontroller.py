"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Set, Union

import cherrypy
from cocktail.controllers import Controller, json_out, read_json

from woost import app
from woost.models import (
    Configuration,
    CreateTranslationPermission
)
from woost.models.utils import get_model_from_dotted_name
from woost.admin.dataimport import Import
from woost.admin.dataexport import Export


class DefaultsController(Controller):

    @json_out
    def __call__(
            self,
            model_name: str,
            locales: Set[str] = (),
            slots: bool = False):

        if not model_name:
            raise cherrypy.HTTPError(400, "No model specified")

        model = get_model_from_dotted_name(model_name)
        locales = self._resolve_locales(locales)

        obj = model()
        data = read_json()

        for locale in locales:
            app.user.require_permission(
                CreateTranslationPermission,
                language=locale
            )
            obj.new_translation(locale)

        Import(data, obj)
        obj.require_id()

        export = Export(include_slots=bool(slots))
        export.languages = locales
        state = export.export_object(obj)
        return state

    def _resolve_locales(self, locales: Union[str, Set[str]]) -> Set[str]:

        if isinstance(locales, str):
            locales = locales.split()

        app_languages = Configuration.instance.languages

        for locale in locales:
            if locale not in app_languages:
                raise cherrypy.HTTPError(400, "Unknown locale: " + locale)

        return locales

