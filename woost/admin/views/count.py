"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import Any, Callable, Iterable, Sequence
from collections import Counter

from cocktail import schema
from cocktail.javascriptserializer import JS
from cocktail.persistence import Query

from woost.models import Item
from woost.models.utils import get_model_dotted_name
from woost.admin.dataexport import Export
from .views import View

CountFunction = Callable[[Query], Counter]


class CountExport(Export):

    def __init__(self, group_column: schema.Member, count_func: CountFunction, **kwargs):
        super().__init__(**kwargs)
        self.group_column = group_column
        self.count_func = count_func

    def get_results(self):
        objects, count = self.resolve_results()
        counter = self.count_func(objects)
        return (
            [
                {
                    "group": self.export_member(
                        None,
                        self.group_column,
                        value=group
                    ),
                    "count": group_count
                }
                for group, group_count in counter.most_common()
            ],
            count
        )


class Count(View):

    allows_sorting = False
    allows_member_selection = False
    allows_locale_selection = False
    pagination = False
    export_class = CountExport

    def get_export_parameters(self):
        return {
            "group_column": self.get_group_column(),
            "count_func": self.get_counter
        }

    def get_group_column(self) -> schema.Member:
        raise TypeError("%r doesn't implement get_group_column()" % self)

    def get_counter(self, items: Iterable[Item]) -> Counter:
        return Counter(
            self.get_count_key(item)
            for item in items
        )

    def get_count_key(self, item: Item) -> Any:
        raise TypeError("%r doesn't implement get_count_key()" % self)

    def export_data(self):
        data = super().export_data()
        data["group_column"] = self.export_group_column()
        return data

    def export_group_column(self):
        group_column = self.get_group_column()
        name = group_column.name
        if group_column.schema:
            name = get_model_dotted_name(group_column.schema) + "." + name
        return name


class CountByMember(Count):

    member: schema.Member

    def __init__(self, name: str, member: schema.Member = None, **kwargs):
        super().__init__(name, **kwargs)
        if member is not None:
            self.member = member

    def get_group_column(self) -> schema.Member:
        return self.member

    def get_count_key(self, item: Item) -> Any:
        return item.get(self.member)

