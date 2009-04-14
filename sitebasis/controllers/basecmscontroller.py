#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from urllib import urlencode
import cherrypy
from cocktail.modeling import getter
from cocktail.events import event_handler
from cocktail.controllers import Controller
from sitebasis.models import Site


class BaseCMSController(Controller):

    def _render_template(self):

        # Pass the request context to the template
        cms = self.context["cms"]
        
        self.output.update(
            cms = cms,
            site = Site.main,
            user = cms.authentication.user,
            document = self.context.get("document")
        )

        return Controller._render_template(self)
  
    @getter
    def user(self):
        return self.context["cms"].authentication.user

    def application_uri(self, *args, **kwargs):
        path = (unicode(arg).strip("/") for arg in args)
        uri = (
            self.context["cms"].virtual_path
            + u"/".join(component for component in path if component)
        )

        if kwargs:
            uri += "?" + urlencode(
                dict(
                    (key, value)
                    for key, value in kwargs.iteritems()
                    if not value is None
                ),
                True
            )   
        return uri

    def document_uri(self, *args, **kwargs):
        from styled import styled
        return self.application_uri(
            self.document_resolver.get_path(self.context["document"]),
            *args,
            **kwargs
        )

    def allows(self, **context):
        return self.context["cms"].authorization.allows(**context)

    def restrict_access(self, **context):
        self.context["cms"].authorization.restrict_access(**context)

