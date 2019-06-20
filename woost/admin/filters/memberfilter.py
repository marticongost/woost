"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Type

from cocktail.pkgutils import get_full_name
from cocktail.modeling import underscore_to_capital, camel_to_underscore
from cocktail import schema
from cocktail.schema.expressions import Expression

from .filter import Filter


class MemberFilter(Filter):

    member: schema.Member = None
    member_copy_parameters = {
        "member_group": None,
        "bidirectional": False,
        "editable": schema.EDITABLE
    }
    expression_class: Type[Expression] = None
    multivalue: bool = False
    filter_id_pattern = "members.{MEMBER}.{EXPRESSION}"

    def filter_expression(self) -> Expression:
        return self.expression_class(self.member, self.value)

    @classmethod
    def create_filter_class(
            cls,
            member: schema.Member,
            expression_class: Type[Expression],
            *,
            multivalue: bool = False) -> Type["MemberFilter"]:

        class MemberFilter(cls):
            filter_group = "members." + member.name
            filter_id = cls.get_filter_id(
                expression_class=expression_class,
                member=member
            )

        MemberFilter.__name__ = (
            underscore_to_capital(member.name)
            + "MemberFilter"
        )
        MemberFilter.name = (
            member.get_qualified_name()
            + "admin.filters." + get_full_name(expression_class)
        )
        MemberFilter.member = member
        MemberFilter.multivalue = multivalue
        MemberFilter.add_member(MemberFilter._create_value_member(member))
        MemberFilter.expression_class = expression_class
        return MemberFilter

    @classmethod
    def get_filter_id(
            cls,
            expression_class: Type[Expression],
            member: schema.Member = None) -> str:

        id = cls.filter_id_pattern.replace(
            "{EXPRESSION}",
            cls.get_expression_id(expression_class)
        )

        if member:
            id = id.replace("{MEMBER}", member.name)

        return id

    @classmethod
    def get_expression_id(
            cls,
            expression_class: Type[Expression]) -> str:

        return camel_to_underscore(
            expression_class.__name__.replace("Expression", "")
        )

    @classmethod
    def _create_value_member(cls, member) -> schema.Member:

        params = {
            "name": None,
            "primary": False,
            "required": True,
            "editable": schema.EDITABLE,
            "member_group": None,
            "before_member": None,
            "after_member": None
        }

        if isinstance(member, schema.RelationMember):
            params["bidirectional"] = False

        member = member.copy(**params)

        if cls.multivalue:
            member = schema.Collection(
                items=member,
                min=1,
                request_value_separator=" "
            )

        member.name = "value"
        return member

    @classmethod
    def get_javascript_declaration(
            cls,
            expression_class: Type[Expression],
            *,
            multivalue: bool = False) -> dict:

        return {
            "id": cls.get_expression_id(expression_class),
            "multivalue": multivalue
        }

