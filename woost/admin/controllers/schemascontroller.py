#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.modeling import camel_to_underscore
from cocktail.javascriptserializer import dumps
from cocktail import schema
from cocktail.controllers import Controller, Cached, request_property
from cocktail.persistence import PersistentObject

from woost import app
from woost.admin.schemaexport import get_member_exporter
from woost.admin.views import available_views
from woost.admin.filters import (
    get_filters,
    get_filter_templates_by_member_type,
    MemberFilter
)
from .utils import set_admin_language

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

        models = [
            model
            for model in PersistentObject.schema_tree()
            if model.translation_source is None
            and model.visible
        ]

        # Schema declarations for custom admin filters
        custom_filters = set()
        for model in models:
            for filter_class in get_filters(
                model,
                include_templates=False,
                include_inherited=False,
                include_members=True
            ):
                if not issubclass(filter_class, MemberFilter):
                    custom_filters.add(filter_class)
                    export = get_member_exporter(model)()
                    export.locales = [language]
                    yield export.get_declaration(filter_class).encode("utf-8")

        # Filter templates
        for member_type, filter_templates \
        in get_filter_templates_by_member_type():
            yield (
                b"%s[woost.admin.filters.templates] = ["
                % member_type.ui_member_class.encode("utf-8")
            )
            yield b",".join(
                b"\n    %s"
                % dumps(
                    filter_template.get_javascript_declaration()
                ).encode("utf-8")
                for filter_template in filter_templates
            )
            yield b"\n];\n"

        # Model declarations
        for model in models:
            export = get_member_exporter(model)()
            export.locales = [language]
            yield export.get_declaration(model).encode("utf-8")

        # View declarations
        for view in available_views():
            params = view.export_data()
            yield "woost.admin.views.addView(%s);\n" % dumps(params)

