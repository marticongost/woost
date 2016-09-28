#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
import re
from urllib2 import urlopen
from json import loads
from cocktail import schema
from cocktail.urls import URL
from cocktail.events import event_handler
from woost.models import Publishable, Controller

ISSUU_DOCUMENT_URL_PATTERN = \
    re.compile(r"http://issuu.com/(.+)/docs/([^/\?]+)/?(\d+)?(\?e=(\d+/\d+))?.*")

def extract_issuu_document_metadata(url):
    match = re.match(ISSUU_DOCUMENT_URL_PATTERN, url)
    if match:
        return {
            "username": match.group(1),
            "docname": match.group(2),
            "configid": match.group(5)
        }
    else:
        return {}


class IssuuDocument(Publishable):

    instantiable = True
    default_per_language_publication = True
    type_group = "resource"

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(qname = "woost.issuu_document_controller")
    )

    members_order = [
        "title",
        "issuu_document_url",
        "thumbnail_page"
    ]

    title = schema.String(
        indexed = True,
        normalized_index = True,
        full_text_indexed = True,
        descriptive = True,
        translated = True,
        required = True,
        spellcheck = True,
        member_group = "content"
    )

    issuu_document_url = schema.URL(
        required = True,
        format = ISSUU_DOCUMENT_URL_PATTERN,
        searchable = False,
        member_group = "content"
    )

    thumbnail_page = schema.Integer(
        required = True,
        default = 1,
        min = 1,
        member_group = "content",
        listed_by_default = False
    )

    issuu_document_id = schema.String(
        editable = schema.NOT_EDITABLE,
        unique = True,
        indexed = True,
        searchable = False,
        member_group = "content",
        listed_by_default = False
    )

    issuu_config_id = schema.String(
        editable = schema.NOT_EDITABLE,
        searchable = False,
        member_group = "content",
        listed_by_default = False
    )

    def get_issuu_uri(self, page_number = None):
        if page_number == None:
            page_number = self.thumbnail_page

        return URL(
            u"http://issuu.com/%s/docs/%s/%s?e=%s" % (
                self.issuu_document_username,
                self.issuu_document_name,
                page_number,
                self.issuu_config_id
            )
        )

    def get_uri(
        self,
        path = None,
        parameters = None,
        language = None,
        host = None
    ):
        url = self.get_issuu_uri()

        if host or path or parameters:
            url_path = url.path
            url_query = url.query
            url_host = host or url.hostname

            if path:
                url_path = list(url_path.segments) + path

            if parameters:
                url_query = url_query.fields
                url_query.update(parameters)

            url = url.copy(
                hostname = url_host,
                path = url_path,
                query = url_query
            )

        return url

    @event_handler
    def handle_changed(cls, event):

        item = event.source
        member = event.member

        if member.name == "issuu_document_url":
            item._update_issuu_document_metadata()

    def _update_issuu_document_metadata(self, timeout = 5):
        if self.issuu_document_url:
            metadata = extract_issuu_document_metadata(self.issuu_document_url)
            self.issuu_document_username = metadata.get("username")
            self.issuu_document_name = metadata.get("docname")
            self.issuu_config_id = metadata.get("configid")

            if self.issuu_document_username and self.issuu_document_name:
                response = urlopen(
                    "http://search.issuu.com/api/2_0/document?q=docname:%s&username=%s" % (
                        self.issuu_document_name,
                        self.issuu_document_username
                    ),
                    timeout = timeout
                )
                status = response.getcode()
                body = response.read()
                if status < 200 or status > 299:
                    raise IssuuSearchAPIError(body)

                data = loads(body)
                try:
                    self.issuu_document_id = \
                        data["response"]["docs"][0]["documentId"]
                except (KeyError, IndexError):
                    self.issuu_document_id = None

            if self.issuu_config_id is None:
                url = URL(self.issuu_document_url).merge(query = {"e": 0})
                response = urlopen(url, timeout = timeout)
                status = response.getcode()
                body = response.read()
                if status >= 200 and status <= 299:
                    url = URL(response.geturl())
                    issuu_config_id = url.query.get_value("e")
                    if issuu_config_id:
                        self.issuu_config_id = issuu_config_id[0]

    def is_internal_content(self, language = None):
        return False


class IssuuSearchAPIError(Exception):

    def __init__(self, response):
        Exception.__init__(self, response)
        self.response = response

