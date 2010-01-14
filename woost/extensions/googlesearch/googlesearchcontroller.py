#-*- coding: utf-8 -*-
"""

@author:		Marc Pérez
@contact:		marc.perez@whads.com
@organization:	Whads/Accent SL
@since:			December 2009
"""

import cherrypy
from cocktail.modeling import cached_getter
from woost.controllers import DefaultHandler
from woost.extensions.googlesearch import GoogleSearchExtension

class GoogleSearchController(DefaultHandler):

    @cached_getter
    def output(self):
        query = cherrypy.request.params.get("query")
        page = cherrypy.request.params.get("page") or 0
        results = GoogleSearchExtension.instance.search(query, int(page))

        output = DefaultHandler.output(self)
        output["query"] = query
        output["results"] = results
        return output

