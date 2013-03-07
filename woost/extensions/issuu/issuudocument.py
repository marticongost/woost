#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
import re
from urllib2 import urlopen
from json import loads
from cocktail import schema
from cocktail.events import event_handler
from woost.models import Publishable, Controller

ISSUU_DOCUMENT_URL_PATTERN = re.compile(u"http://issuu.com/(.+)/docs/([^/]+)/?.*")

def extract_issuu_document_metadata(url):
    match = re.match(ISSUU_DOCUMENT_URL_PATTERN, url)
    if match:
        return {
            "username": match.group(1),
            "docname": match.group(2)
        }
    else:
        return {}


class IssuuDocument(Publishable):

    instantiable = True
    default_per_language_publication = True

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(qname = "woost.issuu_document_controller")
    )

    members_order = [
        "title",
        "issuu_document_url",
        "issuu_embed_code",
        "thumbnail_page"
    ]

    title = schema.String(
        indexed = True,
        normalized_index = True,
        full_text_indexed = True,
        descriptive = True,
        translated = True,
        required = True,
        member_group = "content"
    )

    issuu_document_url = schema.URL(
        required = True,
        format = ISSUU_DOCUMENT_URL_PATTERN,
        searchable = False,
        member_group = "content"
    )

    issuu_embed_code = schema.String(
        required = True,
        searchable = False,
        edit_control = "cocktail.html.TextArea",
        member_group = "content",
        listed_by_default = False
    )

    thumbnail_page = schema.Integer(
        required = True,
        default = 1,
        min = 1,
        member_group = "content",
        listed_by_default = False
    )

    issuu_document_id = schema.String(
        editable = False,
        unique = True,
        indexed = True,
        searchable = False,
        member_group = "content",
        listed_by_default = False
    )

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
                except KeyError, IndexError:
                    self.issuu_document_id = None


class IssuuSearchAPIError(Exception):                                                                                                                                                

    def __init__(self, response):
        Exception.__init__(self, response)
        self.response = response

