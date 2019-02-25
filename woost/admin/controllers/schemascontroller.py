#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from json import dumps
import cherrypy
from cocktail.modeling import camel_to_underscore
from cocktail import schema
from cocktail.controllers import Controller, Cached, request_property
from cocktail.persistence import PersistentObject
from woost import app
from woost.admin.schemaexport import SchemaExport
from woost.admin.filters import (
    get_filters,
    get_filters_by_member_type,
    Filter,
    MultiValueFilter
)
from .utils import set_admin_language

_standard_filter_templates = (Filter, MultiValueFilter)

# Invalidate the cache each time new code is loaded
if app.cache:
    app.cache.clear("woost.admin.schemas")


class SchemasController(Cached, Controller):

    @request_property
    def invalidation(self):
        invalidation = Cached.invalidation(self)
        invalidation.depends_on("woost.admin.schemas")

        for role in app.user.iter_roles():
            invalidation.depends_on(role)
            invalidation.depends_on(role.permissions)

        return invalidation

    @request_property
    def cache_key(self):
        return Cached.cache_key(self), app.user.role.id

    def _produce_content(self):

        language = set_admin_language()

        cherrypy.response.headers["Content-Type"] = \
            "application/javascript; charset=utf-8"

        export = SchemaExport()
        export.locales = [language]

        models = [
            model
            for model in PersistentObject.schema_tree()
            if model.translation_source is None
        ]

        # Schema declarations for custom admin filters
        custom_filters = set()
        for model in models:
            for filter_class in get_filters(
                model,
                recursive = False,
                include_members = True
            ):
                if (
                    filter_class.filter_template
                        not in _standard_filter_templates
                    and filter_class not in custom_filters
                ):
                    custom_filters.add(filter_class)
                    yield export.get_declaration(filter_class)

        # Default filters
        for member_type, filter_dfns in get_filters_by_member_type():
            yield (
                "%s[woost.admin.filters.defaultFilters] = {"
                % member_type.ui_member_class
            )
            yield ",".join(
                "\n    %s: %s" % (
                    (
                        filter_id,
                        filter_dfn.template.javascript_class
                    )
                )
                for filter_id, filter_dfn in filter_dfns.iteritems()
            )
            yield "\n};\n"

        # Model declarations
        for model in models:
            yield export.get_declaration(model)

