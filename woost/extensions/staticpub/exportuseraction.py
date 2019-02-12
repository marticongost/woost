#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from woost.models import Publishable
from woost.controllers.backoffice.useractions import UserAction
from .destination import Destination
from .exportpermission import ExportPermission

translations.load_bundle("woost.extensions.staticpub.exportuseraction")


class ExportUserAction(UserAction):
    content_type = Publishable
    show_as_primary_action = "on_content_type"
    min = None
    max = None

    def is_permitted(self, user, target):
        return any(
            user.has_permission(ExportPermission, destination = destination)
            for destination in Destination.select()
        )


ExportUserAction("static_pub_export").register()

