#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
from cocktail import schema
from sitebasis.models.messagestyles import permission_doesnt_match_style
from sitebasis.models.permission import ContentPermission


class TransitionPermission(ContentPermission):
    """Permission to apply a state transition to an item."""

    instantiable = True

    transition = schema.Reference(
        type = "sitebasis.extensions.workflow.transition.Transition",
        related_key = "transition_permissions",
        bidirectional = True
    )

    def match(self, target, transition, verbose = False):
        
        if self.transition and transition is not self.transition:
            print permission_doesnt_match_style("transition doesn't match")
            return False

        return ContentPermission.match(self, target, verbose)

