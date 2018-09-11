#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import json
import cherrypy
from cocktail.translations import translations, get_language
from cocktail.schema.expressions import Self
from cocktail.persistence import PersistentObject, Query
from cocktail.controllers import Controller, get_parameter
from cocktail.controllers.csrfprotection import no_csrf_token_injection
from woost import app
from woost.models import Item, ReadPermission, Configuration
from woost.models.utils import get_model_dotted_name
from woost.admin.models.dataexport import (
    Export,
    PageTreeExport,
    AdminExport
)
from woost.admin.filters import get_filters
from .utils import resolve_object_ref


class ListingController(Controller):

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
        locales = "_object",
        members = None,
        page = None,
        page_size = None,
        search = None,
        relation = None,
        **kwargs
    ):
        model = self._resolve_model(model)
        locales = self._resolve_locales(locales)
        export = self._resolve_export(export, locales)
        rng = self._resolve_range(page, page_size, implicit = not id)
        filters = self._resolve_filters(model, kwargs)
        relation = self._resolve_relation(relation)

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

            if relation:
                raise cherrypy.HTTPError(
                    400,
                    "Can't apply relation constraints when retrieving a "
                    "single element"
                )

            obj = resolve_object_ref(id)

            if not app.user.has_permission(ReadPermission, target = obj):
                raise cherrypy.HTTPError(403, "Unauthorized object access")

            cherrypy.response.headers["Content-Type"] = \
                "application/json; charset=utf-8"
            return json.dumps(export.export_object(obj))

        # Returning a list of objects
        else:
            filter_expressions = []

            if search:
                filter_expressions.append(
                    Self.search(
                        search,
                        match_mode = "prefix",
                        languages =
                            locales
                            or [None] + list(Configuration.instance.languages)
                    )
                )

            if filters:
                for filter in filters:
                    expr = filter.filter_expression()
                    if expr is not None:
                        filter_expressions.append(expr)

            export.model = model
            export.relation = relation
            export.filters = filter_expressions
            export.range = rng
            results, count = export.get_results()

            cherrypy.response.headers["Content-Type"] = \
                "application/json; charset=utf-8"

            html = [u'{"count": {"value": %d, "label": %s}, "records": [\n' % (
                count,
                json.dumps(
                    translations(
                        "woost.admin.controllers.datacontroller.count",
                        model = model,
                        count = count
                    )
                )
            )]

            glue = u""

            for record in results:
                html.append(glue)
                glue = u",\n"
                html.append(json.dumps(record))

            html.append(u"]}")
            return u"".join(html)

    def _resolve_model(self, model_name):

        if not model_name:
            raise cherrypy.HTTPError(400, "No model specified")

        for cls in PersistentObject.schema_tree():
            if get_model_dotted_name(cls) == model_name:
                return cls

        raise cherrypy.HTTPError(404, "Unknown model")

    def _resolve_locales(self, locales):

        if locales == "_object":
            return None

        if isinstance(locales, basestring):
            return locales.split()

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

    def _resolve_relation(self, relation):

        if relation:
            pos = relation.find("-")
            if pos == -1:
                owner = None
                try:
                    model_name, rel_name = relation.rsplit(".", 1)
                    model = self._resolve_model(model_name)
                except ValueError:
                    raise cherrypy.HTTPError(400, "Invalid relation")
            else:
                id = relation[:pos]
                rel_name = relation[pos + 1:]

                try:
                    owner_id = int(id)
                except ValueError:
                    if id.startswith("_"):
                        return None
                    raise cherrypy.HTTPError(400, "Invalid relation owner")

                owner = Item.get_instance(owner_id)
                if owner is None:
                    raise cherrypy.HTTPError(404, "Relation owner not found")

                model = owner.__class__

            member = model.get_member(rel_name)
            if member is None:
                raise cherrypy.HTTPError(404, "Relation not found")

            return member, owner

        return None

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


class DeleteController(Controller):
    pass

