#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import camel_to_underscore, classgetter
from cocktail.pkgutils import get_full_name
from cocktail import schema
from cocktail.schema.expressions import Expression
from threading import Lock

schema.Member.admin_custom_filters = None

_filters = {}


class Filter(schema.SchemaObject):

    filter_id = None
    filter_group = None
    javascript_class = "woost.admin.filters.Filter"
    filter_member_copy_parameters = {
        "member_group": None,
        "bidirectional": False,
        "editable": schema.EDITABLE
    }

    @classgetter
    def parameter_name(self):
        return "filters." + self.filter_id

    @classgetter
    def filter_template(self):
        return None

    def filter_expression(self):
        raise TypeError(
            "%r doesn't define its filter_expression() method" % self
        )

    @classmethod
    def declare(
        cls,
        member_type,
        filter_id,
        *template_args,
        **template_kwargs
    ):
        try:
            member_type_filters = _filters[member_type]
        except KeyError:
            member_type_filters = {}
            _filters[member_type] = member_type_filters

        _filters[member_type][filter_id] = _FilterDefinition(
            filter_id,
            cls,
            template_args,
            template_kwargs
        )

    @classmethod
    def create_member_filter(cls, member, expression_class = None):

        class MemberFilter(cls):

            @classgetter
            def filter_template(self):
                return cls

            @classgetter
            def filter_member(self):
                return member

            @classgetter
            def filter_expression_class(self):
                return expression_class

            def filter_expression(self):
                return expression_class(member, self.value)

        MemberFilter.__name__ = "%s(%s, %s)" % (
            cls.__name__,
            member.get_qualified_name(include_ns = True),
            expression_class.__name__
        )
        MemberFilter.filter_group = "members." + member.name
        MemberFilter.name = "%s.%s.admin.filters.%s" % (
            member.schema.name,
            member.name,
            expression_class.__name__
        )
        MemberFilter.__module__ = member.schema.__module__
        MemberFilter.schema_aliases = [
            "woost.admin.filters.expressions." + get_full_name(expr_cls)
            for expr_cls in expression_class.__mro__
            if expr_cls is not Expression and issubclass(expr_cls, Expression)
        ]

        value_member = cls._create_value_member(member)
        MemberFilter.add_member(value_member)
        return MemberFilter

    @classmethod
    def _create_value_member(cls, member):

        params = {
            "name": "value",
            "primary": False,
            "required": True,
            "editable": schema.EDITABLE,
            "member_group": None,
            "before_member": None,
            "after_member": None
        }

        if isinstance(member, schema.RelationMember):
            params["bidirectional"] = False

        return member.copy(**params)


class MultiValueFilter(Filter):

    javascript_class = "woost.admin.filters.MultiValueFilter"

    @classmethod
    def _create_value_member(cls, member):

        params = {
            "name": None,
            "primary": False,
            "required": False,
            "editable": schema.EDITABLE,
            "member_group": None,
            "before_member": None,
            "after_member": None
        }

        if isinstance(member, schema.RelationMember):
            params["bidirectional"] = False

        return schema.Collection(
            name = "value",
            min = 1,
            items = member.copy(**params)
        )


class _FilterDefinition(object):

    def __init__(self, filter_id, template, template_args, template_kwargs):
        self.__lock = Lock()
        self.__classes = {}
        self.filter_id = filter_id
        self.template = template
        self.template_args = template_args
        self.template_kwargs = template_kwargs

    def get_filter_class(self, member):
        try:
            return self.__classes[member]
        except KeyError:
            with self.__lock:
                try:
                    return self.__classes[member]
                except KeyError:
                    cls = self.template.create_member_filter(
                        member,
                        *self.template_args,
                        **self.template_kwargs
                    )
                    cls.filter_id = "members.%s.%s" % (
                        member.name,
                        self.filter_id
                    )
                    self.__classes[member] = cls
                    return cls


def get_filters_for_member_type(member_type):
    return _filters[member_type]

def get_filters_by_member_type():
    return _filters.iteritems()

def get_filters(member, recursive = True, include_members = True):

    filters = []

    if isinstance(member, schema.Schema):
        if recursive:
            for base in member.bases:
                filters.extend(
                    get_filters(base, include_members = include_members)
                )

        if include_members:
            for child in member.iter_members(recursive = False):
                filters.extend(get_filters(child))
    else:
        for cls in member.__class__.__mro__:

            if not issubclass(cls, schema.Member):
                continue

            try:
                member_type_filters = _filters[cls]
            except KeyError:
                pass
            else:
                for filter_dfn in member_type_filters.itervalues():
                    filters.append(filter_dfn.get_filter_class(member))
                break

    if member.admin_custom_filters:
        filters.extend(member.admin_custom_filters)

    return filters

