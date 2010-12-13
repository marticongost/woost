#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from webconsole import WebConsole
from cocktail.events import event_handler
from cocktail.iteration import first, last
from cocktail.translations import translations, get_language
from cocktail.persistence import PersistentObject
from woost.controllers.documentcontroller import DocumentController
from woost.models import Site, get_current_user
from woost.extensions.webconsole.webconsolepermission \
    import WebConsolePermission


class CMSWebConsole(DocumentController, WebConsole):

    @event_handler
    def handle_traversed(self, event):
        get_current_user().require_permission(WebConsolePermission)

    submit = WebConsole.submit
    submitted = WebConsole.submitted

    def _update_eval_context(self, context):

        WebConsole._update_eval_context(self, context)

        context.update(
            site = Site.main,
            user = get_current_user(),
            language = get_language(),
            translations = translations,
            first = first,
            last = last
        )

        for model in PersistentObject.schema_tree():
            context[model.name] = model

