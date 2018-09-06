#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from woost import app

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']

def get_client():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        app.path("ga-client-secrets.json"),
        SCOPES
    )
    return build("analyticsreporting", "v4", credentials = credentials)

def get_report(client, request_data):
    return client.reports().batchGet(body = request_data).execute()

