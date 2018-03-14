#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import json
import cherrypy
from cocktail.persistence import PersistentObject
from cocktail.controllers import Controller
from woost import app
from woost.models import (
    Configuration,
    CreatePermission,
    CreateTranslationPermission
)
from woost.models.utils import get_model_dotted_name
from woost.admin.models.dataexport import Export


class DefaultsController(Controller):

    def __call__(self, model_name, locales = ()):

        if not model_name:
            raise cherrypy.HTTPError(400, "No model specified")

        model = self._resolve_model(model_name)
        locales = self._resolve_locales(locales)
        app.user.require_permission(CreatePermission, target = model)
        obj = model()

        for locale in locales:
            app.user.require_permission(
                CreateTranslationPermission,
                language = locale
            )
            obj.new_translation(locale)

        cherrypy.response.headers["Content-Type"] = \
            "application/json; charset=utf-8"

        export = Export()
        export.languages = locales
        state = export.export_object(obj)
        return json.dumps(state)

    def _resolve_model(self, model_name):

        for cls in PersistentObject.schema_tree():
            if get_model_dotted_name(cls) == model_name:
                return cls

        raise cherrypy.HTTPError(404, "Unknown model")

    def _resolve_locales(self, locales):

        if isinstance(locales, basestring):
            locales = locales.split()

        app_languages = Configuration.instance.languages

        for locale in locales:
            if locale not in app_languages:
                raise cherrypy.HTTPError(400, "Unknown locale: " + locale)

        return locales

