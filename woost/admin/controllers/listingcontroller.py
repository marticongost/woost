#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import json
import cherrypy
from cocktail.translations import translations, get_language
from cocktail.schema.expressions import Self
from cocktail.controllers import Controller, get_parameter, request_property
from cocktail.controllers.csrfprotection import no_csrf_token_injection
from woost import app
from woost.models import (
    Item,
    ReadPermission,
    ModifyPermission,
    PermissionExpression,
    Configuration
)
from woost.models.utils import (
    get_model_dotted_name,
    get_model_from_dotted_name
)
from woost.admin.dataexport import Export
from woost.admin.dataexport.sitetreeexport import SiteTreeExport
from woost.admin.dataexport.adminexport import AdminExport
from woost.admin.partitioning import parse_partition_parameter
from woost.admin.filters import get_filters
from .utils import resolve_object_ref

undefined = object()


class ListingController(Controller):

    view = None
    default_export = "default"
    exports = {
        "default": Export,
        "site_tree": SiteTreeExport,
        "admin": AdminExport
    }
    default_order = "-last_update_time"
    max_page_size = 10000

    @no_csrf_token_injection
    def __call__(self, **kwargs):

        # Returning a single object
        if self.instance:

            if self.partition:
                raise cherrypy.HTTPError(
                    400,
                    "Can't apply a partition when retrieving a single element"
                )

            if self.range:
                raise cherrypy.HTTPError(
                    400,
                    "Can't apply a range when retrieving a single element"
                )

            if self.search:
                raise cherrypy.HTTPError(
                    400,
                    "Can't search by text when retrieving a single element"
                )

            if self.filters:
                raise cherrypy.HTTPError(
                    400,
                    "Can't apply filters when retrieving a single element"
                )

            if self.relation:
                raise cherrypy.HTTPError(
                    400,
                    "Can't apply relation constraints when retrieving a "
                    "single element"
                )

            if not app.user.has_permission(
                ReadPermission,
                target = self.instance
            ):
                raise cherrypy.HTTPError(403, "Unauthorized object access")

            cherrypy.response.headers["Content-Type"] = \
                "application/json; charset=utf-8"

            object_data = self.export.export_object(self.instance)
            return json.dumps(object_data)

        # Returning a list of objects
        else:
            self.export.model = self.model
            self.export.base_collection = self.subset
            self.export.relation = self.relation
            self.export.partition = self.partition
            self.export.filters = self.filter_expressions

            if not self.export.fixed_order:
                self.export.order = self.order

            self.export.range = self.range
            results, count = self.export.get_results()

            cherrypy.response.headers["Content-Type"] = \
                "application/json; charset=utf-8"

            html = [
                u'{"count": %s, "records": [\n'
                % json.dumps(self._get_count_object(count))
            ]
            glue = u""

            for record in results:
                html.append(glue)
                glue = u",\n"
                html.append(json.dumps(record))

            html.append(u"]}")
            return u"".join(html)

    @cherrypy.expose
    def ids(self, **kwargs):

        # TODO: hierarchical results [[A1, [A1_1, [A1_2, [A1_2_1, A1_2_2]]]], A2]
        cherrypy.response.headers["Content-Type"] = "application/json"

        if self.instance:
            raise cherrypy.HTTPError(
                400,
                "Can't specify a specific instance when using the "
                "'invalidation' method"
            )

        self.export.model = self.model
        self.export.base_collection = self.subset
        self.export.relation = self.relation
        self.export.partition = self.partition
        self.export.filters = self.filter_expressions
        self.export.order = self.order

        query, count = self.export.resolve_results()

        if self.range:
            query.range = (0, self.range[1])

        return u'{"count": %s, "objects": [%s]}\n' % (
            json.dumps(self._get_count_object(count)),
            ", ".join(str(id) for id in query.execute())
        )

    @cherrypy.expose
    def contains(self, **kwargs):

        cherrypy.response.headers["Content-Type"] = "application/json"

        instance = self.instance
        if instance is None:
            raise cherrypy.HTTPError(400, "No instance specified")

        query = self.model.select()
        query.filters = self.filter_expressions

        if self.partition:
            part_method, part_value = self.partition
            expr = part_method.get_expression(part_value)
            if expr is not None:
                query.add_filter(expr)

        return json.dumps(instance in query)

    @cherrypy.expose
    @no_csrf_token_injection
    def clear_cache(self, **kwargs):

        scope = set()

        if (
            not self.instance
            and not self.subset
            and not self.partition
            and not self.filter_expressions
        ):
            if app.user.has_permission(ModifyPermission, target = self.model):
                scope.update(
                    cls.full_name
                    for cls in self.model.ascend_inheritance(
                        include_self = True
                    )
                )
        elif self.instance:
            if app.user.has_permission(
                ModifyPermission,
                target = self.instance
            ):
                scope.update(self.instance.get_cache_invalidation_scope())
        else:
            if self.relation:
                member, owner = self.relation
                query = member.select_constraint_instances(parent = owner)
            else:
                query = self.model.select()

            query.base_collection = self.subset
            query.add_filter(PermissionExpression(app.user, ReadPermission))
            query.add_filter(PermissionExpression(app.user, ModifyPermission))

            for expr in self.filter_expressions:
                query.add_filter(expr)

            if self.partition:
                part_method, part_value = self.partition
                expr = part_method.get_expression(part_value)
                if expr is not None:
                    query.add_filter(expr)

            for obj in query:
                scope.update(obj.get_cache_invalidation_scope())

        if scope:
            app.cache.clear(scope)

        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps(list(scope))

    @request_property
    def model(self):

        model_name = cherrypy.request.params.get("model")

        if model_name:
            model = get_model_from_dotted_name(model_name)
            if model:
                return model
            else:
                raise cherrypy.HTTPError(400, "Unknown model")

        model = self.view and self.view.model
        if model:
            return model

        raise cherrypy.HTTPError(400, "No model specified")

    @request_property
    def instance(self):

        id = cherrypy.request.params.get("id")

        if id:
            return resolve_object_ref(id)

        return None

    @request_property
    def subset(self):
        subset = cherrypy.request.params.get("subset")
        if subset:
            return [resolve_object_ref(id) for id in subset.split()]
        else:
            return None

    @request_property
    def locales(self):

        value = cherrypy.request.params.get("locales", "_object")

        if value == "_object":
            return None

        if isinstance(value, basestring):
            return value.split()

        return value or [get_language()]

    @request_property
    def export(self):

        export_class = cherrypy.request.params.get(
            "export",
            self.view and self.view.export_class
            or self.default_export
        )

        if isinstance(export_class, basestring):
            try:
                export_class = self.exports[export_class]
            except KeyError:
                raise cherrypy.HTTPError(400, "Invalid export")

        if not export_class:
            raise ValueError("Missing export class")

        return export_class(languages = self.locales)

    @request_property
    def order(self):
        order = cherrypy.request.params.get("order", self.default_order)

        if order:
            if not self.model.get_member(order.lstrip("-")):
                raise cherrypy.HTTPError(400, "Invalid order criteria")

        return order

    @request_property
    def range(self):

        get_param = cherrypy.request.params.get
        page = get_param("page") or None
        page_size = get_param("page_size") or None

        # Disable implicit paging on requests for a single object
        if get_param("id") and not page and not page_size:
            return None

        if page_size is None:
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

    @request_property
    def partition(self):
        value = cherrypy.request.params.get("partition")
        if value:
            partition = parse_partition_parameter(value)
            if not partition:
                raise cherrypy.HTTPError(400, "Invalid partition: " + value)
            return partition
        else:
            return None

    @request_property
    def search(self):
        return cherrypy.request.params.get("search")

    @request_property
    def filters(self):

        filters = []
        get_param = cherrypy.request.params.get

        for filter_class in get_filters(self.model):
            param_value = get_param(filter_class.parameter_name)
            if param_value is not None:
                filter = self._parse_filter(filter_class, param_value)
                if filter:
                    filters.append(filter)

        return filters

    @request_property
    def filter_expressions(self):

        filter_expressions = []

        if self.search:
            filter_expressions.append(
                Self.search(
                    self.search,
                    match_mode = "prefix",
                    languages =
                        self.locales
                        or [None] + list(Configuration.instance.languages)
                )
            )

        for filter in self.filters:
            expr = filter.filter_expression()
            if expr is not None:
                filter_expressions.append(expr)

        return filter_expressions

    @request_property
    def relation(self):

        relation = cherrypy.request.params.get("relation")

        if relation:
            pos = relation.find("-")
            if pos == -1:
                owner = None

                try:
                    model_name, rel_name = relation.rsplit(".", 1)
                except ValueError:
                    raise cherrypy.HTTPError(400, "Invalid relation spec")

                model = get_model_from_dotted_name(model_name)
                if model is None:
                    raise cherrypy.HTTPError(400, "Invalid related model")
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

    def _get_count_object(self, count):

        if self.partition:
            count_obj = self._export_count(count[0][1])
            count_obj["partitions"] = [
                self._export_count(part_count, part_value)
                for part_value, part_count in count
            ]
        else:
            count_obj = self._export_count(count)

        return count_obj

    def _export_count(self, count, partition_value = undefined):

        count_obj = {
            "value": count,
            "label": translations(
                "woost.admin.controllers.datacontroller.count",
                model = self.model,
                count = count
            )
        }

        if partition_value is not undefined:
            method = self.partition[0]
            count_obj["partition"] = method.serialize_value(partition_value)

        return count_obj

