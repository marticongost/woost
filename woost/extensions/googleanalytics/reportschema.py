#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from cocktail.dateutils import CalendarPage
from woost import app
from woost.models import Publishable
from .view import View

translations.load_bundle("woost.extensions.googleanalytics.reportschema")

# Base schema

report_schema = schema.Schema(
    "woost.extensions.googleanalytics.reportschema.ReportSchema",
    members = [
        schema.Reference(
            "view",
            type = View,
            required = True
        ),
        schema.Date(
            "start_date",
            required = True
        ),
        schema.Date(
            "end_date",
            required = True
        ),
        schema.Reference(
            "source_publishable",
            type = Publishable
        )
    ]
)

report_schema["end_date"].min = report_schema["start_date"]

# Form schema

report_form_schema = report_schema.copy(
    name = "woost.extensions.googleanalytics.reportschema.ReportFormSchema",
)

report_form_schema["view"].default = \
    schema.DynamicDefault(lambda: View.select()[0])

report_form_schema["start_date"].default = \
    schema.DynamicDefault(lambda: (CalendarPage.current() - 1).start())

report_form_schema["end_date"].default = \
    schema.DynamicDefault(lambda: CalendarPage.current().start())

report_form_schema["source_publishable"].enumeration = \
    lambda ctx: [app.publishable]

report_form_schema["source_publishable"].edit_control = \
    "woost.extensions.googleanalytics.SourcePublishableSelector"

