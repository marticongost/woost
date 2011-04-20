#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Publishable
from woost.controllers.backoffice.useractions import UserAction
from woost.extensions.facebookpublication.facebookpublicationpermission \
    import FacebookPublicationPermission


class FBPublishUserAction(UserAction):
 
    content_type = Publishable

    included = frozenset([
        ("content", "toolbar"),
        ("collection", "toolbar", "integral"),
        "item_buttons"
    ])

    excluded = frozenset([
        "selector",
        "new_item",
        "calendar_content_view",
        "workflow_graph_content_view",
        "changelog"
    ])

    max = None
    
    def is_permitted(self, user, target):
        return user.has_permission(FacebookPublicationPermission, target = target)


FBPublishUserAction("fbpublish").register()

