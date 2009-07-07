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
    """Base class for all CMS controllers."""

    def _render_template(self):

        # Pass the request context to the template
        cms = self.context["cms"]
        cms.producing_output(
            controller = self,
            output = self.output
        )

        return Controller._render_template(self)
 
    @getter
    def user(self):
        """Obtains the currently logged in user.
        
        This is just a convenience property that provides quick access to the
        analogous property in the 
        L{authentication<sitebasis.controllers.authentication.AuthenticationModule>}
        module from any controller.
                
        If no user is logged in, the 'sitebasis.anonymous' role is returned.

        @rtype: L{Agent<sitebasis.models.Agent>}
        """
        return self.context["cms"].authentication.user

    def application_uri(self, *args, **kwargs):
        """Builds an absolute URI from a set of path components and parameters.
        
        @param args: A set of path components, relative to the application
            root. Takes any object that can be expressed as an unicode string.

        @param kwargs: A set of query string parameters to be included on the
            generated URI.
        
        @return: The generated absolute URI.
        @rtype: unicode
        """
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
        """Builds an URI relative to the location of the current document.
        
        @param args: A set of path components that will be appended to the
            document's URI. Takes any object that can be expressed as an
            unicode string.

        @param kwargs: A set of query string parameters to be included on the
            generated URI.
        
        @return: The generated absolute URI.
        @rtype: unicode
        """
        resolver = self.context["cms"].document_resolver
        document = self.context["document"]
        uri = resolver.get_path(document)

        if uri is None:
            return None
        
        return self.application_uri(
            uri,
            *args,
            **kwargs
        )

    def allows(self, **context):
        """Requests validation of a security context.

        This is just a convenience method to quickly access the analogous
        method on the
        L{authorization<sitebasis.controllers.authorization.AuthorizationModule>}
        module from any controller.

        @return: True if access is granted, False otherwise.
        @rtype: bool
        """
        return self.context["cms"].authorization.allows(**context)

    def restrict_access(self, **context):
        """Raises an exception if a security context fails to validate.

        This is just a convenience method to quickly access the analogous
        method on the
        L{authorization<sitebasis.controllers.authorization.AuthorizationModule>}
        module from any controller.

        @raise L{AccessDeniedError<sitebasis.models.AccessDeniedError>}: Raised
            if access can't be granted for the requested security context.
        """
        self.context["cms"].authorization.restrict_access(**context)

