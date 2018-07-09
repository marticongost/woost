#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from copy import deepcopy
import json
import cherrypy
from cocktail.controllers import Controller, get_parameter
from woost import app
from woost.models import Configuration
from .reportschema import report_schema
from .reports import get_client, get_report
from .readreportspermission import ReadReportsPermission
from .customdefinition import GoogleAnalyticsCustomDefinition


class ReportController(Controller):

    def __call__(self, **kwargs):

        app.user.require_permission(ReadReportsPermission)
        form_data = get_parameter(report_schema, errors = "raise")

        config = Configuration.instance
        custom_defs = config.google_analytics_custom_definitions

        base_report = {
            "viewId": form_data["view"].identifier,
            "dateRanges": [{
                "startDate": form_data["start_date"].strftime("%Y-%m-%d"),
                "endDate": form_data["end_date"].strftime("%Y-%m-%d")
            }],
            "metrics": [{"expression": "ga:totalEvents"}],
            "dimensions": [{"name": "ga:eventLabel"}],
            "samplingLevel": "LARGE",
            "pageSize": 10000
        }

        source_publishable = form_data.get("source_publishable")

        if source_publishable:
            publishable_custom_def = GoogleAnalyticsCustomDefinition.get_instance(
                qname = "woost.extensions.googleanalytics."
                        "default_custom_definitions.publishable"
            )
            base_report["dimensionFilterClauses"] = {
                "operator": "AND",
                "filters": [
                    {
                        "dimensionName":
                            "ga:dimension%d"
                            % (custom_defs.index(publishable_custom_def) + 1),
                        "operator": "PARTIAL",
                        "expressions": [
                            "--%d--" % source_publishable.id
                        ]
                    }
                ]
            }

        reports = [base_report]

        target_custom_def = GoogleAnalyticsCustomDefinition.get_instance(
            qname = "woost.extensions.googleanalytics."
            "default_custom_definitions.target"
        )

        if target_custom_def:
            target_report = deepcopy(base_report)
            target_report["dimensions"].append(
                {"name": "ga:dimension%d"
                 % (custom_defs.index(target_custom_def) + 1)}
            )
            reports.append(target_report)

        request_data = {"reportRequests": reports}
        client = get_client()
        report = get_report(client, request_data)

        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps(report)

