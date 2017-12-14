#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import json
import cherrypy
from cocktail.translations import translations, set_language, get_language
from cocktail.schema.expressions import Self
from cocktail.persistence import PersistentObject, Query
from cocktail.controllers import Controller, get_parameter
from cocktail.controllers.csrfprotection import no_csrf_token_injection
from woost import app
from woost.models import ReadPermission
from woost.models.utils import get_model_dotted_name
from woost.admin.models.dataexport import (
    Export,
    PageTreeExport,
    AdminExport
)
from woost.admin.filters import get_filters

translations.load_bundle("woost.admin.controllers.datacontroller")


class DataController(Controller):

    default_export = "default"
    exports = {
        "default": Export,
        "page_tree": PageTreeExport,
        "admin": AdminExport
    }
    max_page_size = 100

    @no_csrf_token_injection
    def __call__(
        self,
        model,
        id = None,
        export = None,
        locales = None,
        members = None,
        page = None,
        page_size = None,
        search = None,
        **kwargs
    ):
        language = (
            app.user.prefered_language
            or app.publishable.default_language
        )
        set_language(language)

        model = self._resolve_model(model)
        locales = self._resolve_locales(locales)
        export = self._resolve_export(export, locales)
        rng = self._resolve_range(page, page_size, implicit = not id)
        filters = self._resolve_filters(model, kwargs)

        # Returning a single object
        if id:
            if rng:
                raise cherrypy.HTTPError(
                    400,
                    "Can't apply a range when retrieving a single element"
                )

            if search:
                raise cherrypy.HTTPError(
                    400,
                    "Can't search by text when retrieving a single element"
                )

            if filters:
                raise cherrypy.HTTPError(
                    400,
                    "Can't apply filters when retrieving a single element"
                )

            try:
                id = int(id)
            except ValueError:
                raise cherrypy.HTTPError(400, "Non numeric ID")
            else:
                obj = model.get_instance(id)
                if obj is None:
                    raise cherrypy.HTTPError(404, "Object not found")

                if not app.user.has_permission(ReadPermission, target = obj):
                    raise cherrypy.HTTPError(403, "Unauthorized object access")

                cherrypy.response.headers["Content-Type"] = \
                    "application/json; charset=utf-8"
                yield json.dumps(export.export_object(obj))

        # Returning a list of objects
        else:
            results = export.select_root(model)
            results.verbose = True

            if search:
                results.add_filter(
                    Self.search(
                        search,
                        match_mode = "prefix",
                        languages = locales
                    )
                )

            if filters:
                for filter in filters:
                    expr = filter.filter_expression()
                    if expr is not None:
                        results.add_filter(expr)

            count = len(results)

            if rng:
                if isinstance(results, Query):
                    results.range = rng
                else:
                    results = results[rng[0]:rng[1]]

            cherrypy.response.headers["Content-Type"] = \
                "application/json; charset=utf-8"

            yield u'{"count": {"value": %d, "label": %s}, ' % (
                count,
                json.dumps(
                    translations(
                        "woost.admin.controllers.datacontroller.count",
                        model = model,
                        count = count
                    )
                )
            )

            yield u'"records": [\n'
            glue = u""

            for obj in results:
                yield glue
                glue = u",\n"
                yield json.dumps(export.export_object(obj))

            yield u"]}"

    def _resolve_model(self, model_name):

        if not model_name:
            raise cherrypy.HTTPError(400, "No model specified")

        for cls in PersistentObject.schema_tree():
            if get_model_dotted_name(cls) == model_name:
                return cls

        raise cherrypy.HTTPError(404, "Unknown model")

    def _resolve_locales(self, locales):
        return locales or [get_language()]

    def _resolve_export(self, export_id, languages):

        if export_id:
            try:
                export_class = self.exports[export_id]
            except KeyError:
                raise cherrypy.HTTPError(400, "Invalid export")
        else:
            export_id = self.default_export
            export_class = self.exports.get(export_id)

        if not export_class:
            raise ValueError("Missing export class")

        if isinstance(languages, basestring):
            languages = languages.split(",")

        return export_class(languages = languages)

    def _resolve_range(self, page, page_size, implicit = False):

        if page == "":
            page = None

        if page_size == "":
            page_size = None

        if page_size is None and implicit:
            page_size = self.max_page_size

        if page is None and page_size is None:
            return None

        if page is None and page_size is not None:
            page = 0

        if page is not None and page_size is None:
            raise cherrypy.HTTPError(
                400,
                "Can't set page without setting page size as well"
            )

        if not isinstance(page, int):
            try:
                page = int(page)
                assert page >= 0
            except ValueError, AssertionError:
                raise cherrypy.HTTPError(400, "Invalid page number")

        if not isinstance(page_size, int):
            try:
                page_size = int(page_size)
                assert page_size > 0
            except ValueError, AssertionError:
                raise cherrypy.HTTPError(400, "Invalid value for page_size")

        start = page_size * page
        return (start, start + page_size)

    def _resolve_filters(self, model, params):

        filters = []

        for filter_class in get_filters(model):
            param_value = params.get(filter_class.parameter_name)
            if param_value is not None:
                filter = self._parse_filter(filter_class, param_value)
                if filter:
                    filters.append(filter)

        return filters

    def _parse_filter(self, filter_class, param_value):

        # Filters with multiple members must be JSON encoded
        for i, member in enumerate(filter_class.iter_members()):
            if i > 0:
                source = json.loads(param_value)
                break
        # Single member filters should provide a single value
        else:
            source = {member.name: param_value}

        filter = filter_class()
        get_parameter(
            filter_class,
            target = filter,
            source = source.get,
            undefined = "set_default",
            implicit_booleans = False,
            errors = "ignore"
        )
        return filter if filter_class.validate(filter) else None

