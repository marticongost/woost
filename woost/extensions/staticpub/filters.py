#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import cached_getter
from cocktail.translations import translations
from cocktail import schema
from cocktail.controllers.userfilter import UserFilter, user_filters_registry
from cocktail.schema.expressions import Expression, Self
from woost.models import LocaleMember, Publishable
from .destination import Destination

translations.load_bundle("woost.extensions.staticpub.filters")


class HasPendingChangesExpression(Expression):

    def __init__(self, publishable, destination, language = None):
        Expression.__init__(
            self,
            publishable,
            destination,
            language
        )

    @property
    def publishable(self):
        return self.operands[0]

    @property
    def destination(self):
        return self.operands[1]

    @property
    def language(self):
        return self.operands[2]

    def op(self, publishable, destination, language):
        return destination.has_pending_tasks(publishable, language)

    def resolve_filter(self, query):

        if self.operands[0] is Self:
            destination = self.operands[1].eval()
            language = self.operands[2].eval()

            if language is None:
                def impl(dataset):
                    dataset.intersection_update(
                        publishable_id
                        for action, publishable_id, lang
                        in destination.iter_pending_tasks()
                    )
                    return dataset
                return ((-1, -1), impl)
            else:
                def impl(dataset):
                    dataset.intersection_update(
                        publishable_id
                        for action, publishable_id, lang
                        in destination.iter_pending_tasks()
                        if lang == language
                    )
                    return dataset
                return ((-1, 1), impl)
        else:
            return ((0, 0), None)


class HasPendingChangesUserFilter(UserFilter):

    id = "static_pub_pending"

    @cached_getter
    def schema(self):
        return schema.Schema(
            "woost.extensions.staticpub.filters.HasPendingChangesUserFilter",
            members = [
                schema.Reference(
                    "destination",
                    type = Destination,
                    required = True,
                    search_control = "cocktail.html.DropdownSelector"
                ),
                LocaleMember("language")
            ]
        )

    @property
    def expression(self):
        if self.destination:
            return HasPendingChangesExpression(
                Self,
                self.destination,
                self.language
            )


user_filters_registry.add(Publishable, HasPendingChangesUserFilter)

