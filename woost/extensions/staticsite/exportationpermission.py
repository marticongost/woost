#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			March 2010
"""
from cocktail.translations import translations
from cocktail import schema
from cocktail.html import templates
from woost.models.messagestyles import permission_doesnt_match_style
from woost.models.permission import Permission


class ExportationPermission(Permission):
    """Permission to execute a site's exportation to a destination."""

    instantiable = True

    destination = schema.Reference(
        type = "woost.extensions.staticsite.staticsitedestination.StaticSiteDestination",
        related_key = "destination_permissions",
        bidirectional = True,
        edit_control = "cocktail.html.DropdownSelector"
    )

    def match(self, user, destination, verbose = False):

        if self.destination and destination is not self.destination:
            if verbose:
                print permission_doesnt_match_style("destination doesn't match")
            return False

        return Permission.match(self, user = user, verbose = verbose)

