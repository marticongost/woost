#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.controllers import request_property
from woost.controllers.backoffice.useractions import get_user_action
from woost.controllers.backoffice.editcontroller import EditController
from woost.models import (
    get_current_user,
    Item, 
    ReadPermission,
    ReadMemberPermission
)


class ReferencesController(EditController):

    view_class = "woost.views.BackOfficeReferencesView"

    @request_property
    def references(self):
        return list(self._iter_references(self.stack_node.item))

    def _iter_references(self, obj):
        for member in obj.__class__.members().itervalues():
            if (
                isinstance(member, schema.RelationMember) 
                and member.related_end
                and member.related_end.visible_in_reference_list
                and issubclass(member.related_type, Item)
                and member.related_type.visible
                and not member.integral
            ):
                value = obj.get(member)
                if value:
                    if isinstance(member, schema.Reference):
                        if self._should_include_reference(value, member.related_end):
                            yield value, member.related_end
                    elif isinstance(member, schema.Collection):
                        for item in value:
                            if self._should_include_reference(item, member.related_end):
                                yield item, member.related_end
    
    def _should_include_reference(self, referrer, relation):
        user = get_current_user()
        return (
            relation.visible
            and user.has_permission(ReadPermission, target = referrer)
            and user.has_permission(ReadMemberPermission, member = relation)
        )

    @request_property
    def output(self):
        output = EditController.output(self)
        output.update(
            selected_action = get_user_action("references"),
            references = self.references
        )
        return output

