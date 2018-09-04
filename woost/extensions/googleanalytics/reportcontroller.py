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

        reports = []

        base_report = {
            "viewId": form_data["view"].identifier,
            "dateRanges": [{
                "startDate": form_data["start_date"].strftime("%Y-%m-%d"),
                "endDate": form_data["end_date"].strftime("%Y-%m-%d")
            }],
            "samplingLevel": "LARGE",
            "pageSize": 10000
        }

        source_publishable = form_data.get("source_publishable")

        if source_publishable:
            publishable_custom_def = GoogleAnalyticsCustomDefinition.get_instance(
                qname = "woost.extensions.googleanalytics."
                        "default_custom_definitions.publishable"
            )
            publishable_dim = (
                "ga:dimension%d"
                    % (custom_defs.index(publishable_custom_def) + 1)
            )
            base_report["dimensionFilterClauses"] = {
                "operator": "AND",
                "filters": [
                    {
                        "dimensionName": publishable_dim,
                        "operator": "PARTIAL",
                        "expressions": ["--%d--" % source_publishable.id]
                    }
                ]
            }

        agg_report = deepcopy(base_report)
        agg_report["dimensions"] = [{"name": "ga:eventLabel"}]
        agg_report["metrics"] = [{"expression": "ga:totalEvents"}]
        reports.append(agg_report)

        target_custom_def = GoogleAnalyticsCustomDefinition.get_instance(
            qname = "woost.extensions.googleanalytics."
            "default_custom_definitions.target"
        )

        if target_custom_def:
            target_report = deepcopy(agg_report)
            target_report["dimensions"].append(
                {"name": "ga:dimension%d"
                 % (custom_defs.index(target_custom_def) + 1)}
            )
            reports.append(target_report)

        if source_publishable:
            page_report = deepcopy(base_report)
            page_report["dimensions"] = [{"name": publishable_dim}]
            page_report["metrics"] = [{"expression": "ga:pageviews"}]
            reports.append(page_report)

        request_data = {"reportRequests": reports}
        client = get_client()
        report = get_report(client, request_data)

        cherrypy.response.headers["Content-Type"] = "application/json"
        return json.dumps(report)

