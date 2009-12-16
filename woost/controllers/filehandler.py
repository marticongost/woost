#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cherrypy.lib.static import serve_file
from cocktail.controllers import RequestHandler, context


class FileHandler(RequestHandler):

    def __call__(self):
        document = context["document"]
        return serve_file(
                    document.file_path,
                    content_type = document.mime_type)

