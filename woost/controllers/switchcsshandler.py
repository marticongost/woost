#-*- coding: utf-8 -*-
u"""Adds support for the Switch CSS preprocessor.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
try:
    from switch.StyleSheet import SSSStyleSheet
except ImportError:
    pass
else:
    import os
    from mimetypes import add_type
    import cherrypy
    from cherrypy.lib import cptools, http
    from cocktail.cache import Cache
    from woost.controllers.filecontroller import handles_mime_type

    add_type("text/switchcss", ".sss")

    class SSSCache(Cache):

        def load(self, key):
            return SSSStyleSheet(key).cssText

        def _is_current(self, entry):
            
            if not Cache._is_current(self, entry):
                return False

            # Reprocess modified files
            # TODO: take 'include' directives into account, recursively
            # Sadly, Switch doesn't seem to expose this information
            try:
                mtime = os.stat(entry.key).st_mtime
            except:
                return False
            else:
                return entry.creation >= mtime

    cache = SSSCache()

    @handles_mime_type("text/switchcss")
    def switch_css_handler(controller, file):
        
        from cocktail.styled import styled
        print styled(file.file_path, "pink")

        try:    
            css = cache.request(file.file_path)
        except:
            raise cherrypy.NotFound()

        cherrypy.response.headers["Content-Type"] = "text/css"
        cherrypy.response.headers["Last-Modified"] = \
            http.HTTPDate(cache[file.file_path].creation)
        cptools.validate_since()
        cherrypy.response.body = [css]

