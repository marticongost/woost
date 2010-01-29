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
from woost.models import (
    Publishable,
    Language
)
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from woost.extensions.staticsite.staticsiteexporter import StatusTracker


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

        return schema.Schema("ExportStaticSite", members = [
            schema.Reference(
                "exporter",
                type =
                    "woost.extensions.staticsite.staticsiteexporter."
                    "StaticSiteExporter",
                required = True,
                enumeration = extension.exporters,
                edit_control =
                    "cocktail.html.RadioSelector"
                    if len(extension.exporters) > 1
                    else "cocktail.html.HiddenInput",
                default = extension.exporters[0]
            ),
            schema.Collection(
                "selection",
                items = schema.Reference(
                    type = Publishable,
                    relation_constraints = 
                        [Publishable.exportable_as_static_content.equal(True)]
                ),
                default = schema.DynamicDefault(lambda:
                    list(Publishable.select(
                        Publishable.exportable_as_static_content.equal(True)
                    ))
                )
            ),
            schema.Collection(
                "language",
                items = schema.String(
                    enumeration = site_languages,
                    translate_value = translations
                ),
                edit_control = 
                    "cocktail.html.CheckList"
                    if len(site_languages) > 1
                    else "cocktail.html.HiddenInput",
                default = site_languages
            ),
            schema.Boolean(
                "update_only",
                required = True,
                default = True
            ),
            schema.Boolean(
                "include_resources",
                default = False,
                required = True
            )            
        ])

    def submit(self): 
        FormControllerMixin.submit(self)
        
        export_events = []
        tracker = StatusTracker()

        @when(tracker.item_processed)
        def handle_item_processed(event):
            if event.status == "failed":
                event.error_handled = True
            export_events.append(event)

        form = self.form_instance
        form["exporter"].export(
            form["selection"],
            languages = form["language"],
            update_only = form["update_only"],
            status_tracker = tracker
        )
        
        self.output["export_events"] = export_events

