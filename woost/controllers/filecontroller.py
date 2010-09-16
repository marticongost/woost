#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.modeling import classgetter, DictWrapper
import cherrypy
from cocktail.controllers import serve_file
from woost.controllers import BaseCMSController


class FileController(BaseCMSController):
    """A controller that serves the files managed by the CMS."""

    def __call__(self, disposition = "inline"):
        file = self.context["publishable"]
        
        return serve_file(
            file.file_path,
            name = file.file_name,
            content_type = file.mime_type,
            disposition = disposition)

