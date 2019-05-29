"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import classgetter
from cocktail import schema
from cocktail.schema.expressions import Expression


class Filter(schema.SchemaObject):

    filter_id = None
    filter_group = None
    javascript_class = "woost.admin.filters.Filter"

    @classgetter
    def parameter_name(self) -> str:
        return "filters." + self.filter_id

    def filter_expression(self) -> Expression:
        raise TypeError(
            "%r doesn't define its filter_expression() method" % self
        )

