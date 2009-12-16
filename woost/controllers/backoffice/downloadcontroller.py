#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from cherrypy.lib.static import serve_file
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController


class DownloadController(BaseBackOfficeController):

    def __call__(self, **kwargs):

        file = self.context["cms_item"]

        disposition = kwargs.get("disposition")
        if disposition not in ("inline", "attachment"):
            disposition = "inline"

        return serve_file(
                file.file_path,
                name = file.file_name,
                disposition = disposition,
                content_type = file.mime_type)

