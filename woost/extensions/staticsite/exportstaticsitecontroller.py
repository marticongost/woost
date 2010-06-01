#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""
from datetime import datetime
from cStringIO import StringIO
import cherrypy
from cocktail.modeling import cached_getter
from cocktail.events import when
from cocktail.translations import translations
from cocktail import schema
from cocktail.controllers.formcontrollermixin import FormControllerMixin
from cocktail.persistence import datastore
from woost.models import (
    Publishable,
    Language,
    get_current_user
)
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from woost.extensions.staticsite.staticsitedestination import StatusTracker
from woost.extensions.staticsite.exportationpermission import \
    ExportationPermission


class ExportStaticSiteController(
    FormControllerMixin,
    BaseBackOfficeController
):
    view_class = "woost.extensions.staticsite.ExportStaticSiteView"

    @cached_getter
    def form_model(self):
        
        from woost.extensions.staticsite import StaticSiteExtension
        extension = StaticSiteExtension.instance        
        
        site_languages = Language.codes

        def allowed_destinations():
            return [
                destination 
                for destination in extension.destinations 
                if get_current_user().has_permission(
                    ExportationPermission,
                    destination = destination
                )
            ]

        return schema.Schema("ExportStaticSite", members = [
            schema.Reference(
                "destination",
                type =
                    "woost.extensions.staticsite.staticsitedestination."
                    "StaticSiteDestination",
                required = True,
                enumeration = lambda ctx: allowed_destinations(),
                edit_control =
                    "cocktail.html.RadioSelector"
                    if len(allowed_destinations()) > 1
                    else "cocktail.html.HiddenInput",
                default = schema.DynamicDefault(lambda: allowed_destinations()[0])
            ),
            schema.Boolean(
                "update_only",
                required = True,
                default = True
            )            
        ])

    def submit(self): 
        FormControllerMixin.submit(self)
        
        export_events = []
        tracker = StatusTracker()

        @when(tracker.file_processed)
        def handle_file_processed(event):
            if event.status == "failed":
                event.error_handled = True
            export_events.append(event)

        form = self.form_instance

        user = get_current_user()
        user.require_permission(
            ExportationPermission,
            destination = form["destination"]
        )
        form["destination"].export(
            update_only = form["update_only"],
            status_tracker = tracker
        )
        
        self.output["export_events"] = export_events

        datastore.commit()

