#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cherrypy.lib.static import serve_file
from woost.controllers import BaseCMSController


class FileController(BaseCMSController):
    """A controller that serves the files managed by the CMS."""

    def __call__(self):
        file = self.context["publishable"]
        return serve_file(file.file_path, content_type = file.mime_type)

