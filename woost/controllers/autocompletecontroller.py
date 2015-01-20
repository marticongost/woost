#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.controllers.autocompletecontroller \
    import AutocompleteController as BaseAutocompleteController

from woost.models import (
    Publishable,
    get_current_user,
    ReadPermission,
    PermissionExpression,
    IsAccessibleExpression
)


class AutocompleteController(BaseAutocompleteController):

    publishable_check = True

    def get_items(self):
        items = BaseAutocompleteController.get_items(self)

        if (
            self.publishable_check
            and issubclass(self.member.type, Publishable)
        ):
            items.add_filter(IsAccessibleExpression())
        else:
            items.add_filter(
                PermissionExpression(
                    get_current_user(),
                    ReadPermission
                )
            )

        return items

