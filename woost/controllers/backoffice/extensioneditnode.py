#-*- coding: utf-8 -*-
u"""

@author:		Javier Marrero
@contact:		javier.marrero@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
import cherrypy
from cocktail.events import event_handler
from cocktail.translations import translations
from woost.controllers.backoffice.editstack import EditNode
from woost.controllers.notifications import Notification

translations.load_bundle("woost.controllers.backoffice.extensioneditnode")


class ExtensionEditNode(EditNode):

    def item_saved_notification(self, is_new, change):
        if change and "enabled" in change.changed_members:
            Notification(
                translations(
                    "woost.controllers.backoffice.extensioneditnode."
                    "extension_%s_reload_notice"
                    % ("enabled" if self.item.enabled else "disabled"),
                    extension = self.item
                ),
                "notice",
                transient = False
            ).emit()
        else:
            EditNode.item_saved_notification(self, is_new, change)

