#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.modeling import getter
from cocktail.events import event_handler
from cocktail import schema
from cocktail.controllers import context
from sitebasis.models.resource import Resource

mime_type_categories = {}

for category, mime_types in (
    ("text/plain", ("text",)),
    ("html_resource", (
        "text/css",
        "text/javascript",
        "text/ecmascript",
        "application/javascript",
        "application/ecmascript"
    )),
    ("document", (
        "application/vnd.oasis.opendocument.text",
        "application/vnd.oasis.opendocument.spreadsheet",
        "application/vnd.oasis.opendocument.presentation",
        "application/msword",
        "application/msexcel",
        "application/msaccess",
        "application/mspowerpoint",
        "application/mswrite",
        "application/vnd.ms-excel",
        "application/vnd.ms-powerpoint",
        "application/vnd.ms-project",
        "application/vnd.ms-works",
        "application/vnd.ms-xpsdocument",
        "application/rtf",
        "application/pdf",
        "application/postscript",
        "application/x-latex",
        "application/vnd.oasis.opendocument.database",
        "application/msaccess"
    )),
    ("package", (
        "application/zip",
        "application/x-rar-compressed",
        "application/x-tar",
        "application/x-gtar",
        "application/x-gzip",
        "application/x-bzip",
        "application/x-stuffit",
        "vnd.ms-cab-compressed"
    ))
):
    for mime_type in mime_types:
        mime_type_categories[mime_type] = category


class File(Resource):
 
    instantiable = True

    edit_view = "sitebasis.views.FileFieldsView"

    edit_controller = \
        "sitebasis.controllers.backoffice.filefieldscontroller." \
        "FileFieldsController"

    members_order = [
        "file_name",
        "mime_type"
    ]

    file_name = schema.String(
        required = True,
        editable = False
    )

    mime_type = schema.String(
        required = True,
        editable = False
    )

    file_size = schema.Integer(
        required = True,
        editable = False,
        min = 0
    )

    file_hash = schema.String(
        visible = False
    )

    @getter
    def uri(self):
        return context["cms"].application_uri("files", self.id)

    @getter
    def file_path(self):
        return context["cms"].get_file_upload_path(self.id)

    @event_handler
    def handle_changed(cls, event):
        # Update the 'file_category' member when 'mime_type' is set

        file = event.source

        if event.member.name == "mime_type":
            file.resource_type = \
                file.get_category_from_mime_type(file.mime_type)

    @classmethod
    def get_category_from_mime_type(cls, mime_type):
        """Obtains the file category that best matches the indicated MIME type.
        
        @param mime_type: The MIME type to get the category for.
        @type mime_type: str

        @return: A string identifier with the category matching the indicated
            MIME type (one of 'document', 'image', 'audio', 'video', 'package',
            'html_resource' or 'other').
        @rtype: str
        """
        pos = mime_type.find("/")

        if pos != -1:
            prefix = mime_type[:pos]

            if prefix in ("image", "audio", "video"):
                return prefix
        
        return mime_type_categories.get(mime_type, "other")


# Adapted from a script by Martin Pool, original found at
# http://mail.python.org/pipermail/python-list/1999-December/018519.html
_size_suffixes = [
    (1<<50L, 'Pb'),
    (1<<40L, 'Tb'), 
    (1<<30L, 'Gb'), 
    (1<<20L, 'Mb'), 
    (1<<10L, 'kb'),
    (1, 'bytes')
]

def get_human_readable_file_size(size):
    """Return a string representing the greek/metric suffix of a file size."""
    for factor, suffix in _size_suffixes:
        if size > factor:
            break
    return str(int(size/factor)) + suffix

