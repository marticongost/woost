#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from cocktail.modeling import classgetter, DictWrapper
import cherrypy
from cherrypy.lib.static import serve_file
from woost.controllers import BaseCMSController


class FileController(BaseCMSController):
    """A controller that serves the files managed by the CMS."""

    _mime_type_handlers = {}
    _mime_type_handlers_wrapper = DictWrapper(_mime_type_handlers)

    def __call__(self, disposition = "inline"):
        file = self.context["publishable"]
        
        if disposition not in ("inline", "attachment"):
            raise ValueError("disposition must be either 'inline' or 'attachment', not '%s'" % disposition)
        
        handler = self._mime_type_handlers.get(file.mime_type)

        if handler:
            cherrypy.response.headers["Content-Type"] = file.mime_type
            cherrypy.response.headers["Content-Disposition"] = "%s; filename=%s" % (
                disposition,
                file.file_name
            )
            handler(self, file)
            return cherrypy.response.body
        else:
            return serve_file(
                file.file_path,
                name = file.file_name,
                content_type = file.mime_type,
                disposition = disposition)

    @classgetter
    def mime_type_handlers(cls):
        """A read only dictionary mapping MIME types to their handler
        functions.
        """
        return cls._mime_type_handlers_wrapper

    @classmethod
    def add_mime_type_handler(cls, mime_type, handler):
        """Registers a function (a 'handler') to serve files of the specified
        MIME type.

        :param mime_type: The MIME type to register the function for. Can be a
            specific MIME type (ie. image/png, text/css) or a general MIME
            category (ie. image, text).
        :type mime_type: str

        :param handler: The function that produces the output for files of the
            indicated MIME type. It should take two positional arguments: the
            `file controller <FileController>` that is invoking it, and a
            reference to the `~woost.models.File` object that the handler
            should serve to the current HTTP response.
        :type handler: callable
        """
        cls._mime_type_handlers[mime_type] = handler

    @classmethod
    def get_mime_type_handler(cls, mime_type):
        """Get the handler for the specified MIME type.
        
        :param mime_type: The MIME type to evaluate. Can be a specific MIME
            type (ie. image/png, text/css) or a general MIME category 
            (ie. image, text).
        :type mime_type: str
        
        :return: The handler for the specified MIME type, or None if there is
            no registered handler for the specified type.
        :rtype: callable
        """
        handler = self._mime_type_handlers.get(mime_type)

        if handler is None:
            try:
                category, identifier = mime_type.split("/")
            except:
                pass
            else:
                handler = self._mime_type_handlers.get(category)

        return handler


def handles_mime_type(mime_type):
    """A convenience decorator that makes it easier to
    `define MIME type handlers<FileController.add_mime_type_handler>`.
    """
    def decorator(function):
        FileController.add_mime_type_handler(mime_type, function)
        return function

    return decorator

