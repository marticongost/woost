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


class ExtensionEditNode(EditNode):

    @event_handler
    def handle_committed(cls, event):
        extension = event.source.item
        change = event.changeset.changes.get(extension.id)
                
        if change and "enabled" in change.changed_members:
            cherrypy.request.handler_chain[-1].notify_user(
                translations(
                    "woost.controllers.backoffice.ExtensionEditNode "
                    "%s extension needs reloading"
                    % ("enabled" if extension.enabled else "disabled"),
                    extension = extension
                ),
                "notice",
                transient = False
            )

