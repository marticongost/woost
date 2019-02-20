#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from types import GeneratorType
from time import time
import cherrypy
from cocktail.caching import CacheKeyError
from cocktail.translations import get_language, translations
from cocktail.controllers import (
    request_property,
    Cached,
    redirect,
    get_request_url
)
from woost import app
from woost.controllers import BaseCMSController


class PublishableController(BaseCMSController, Cached):
    """Base controller for all publishable items (documents, files, etc)."""

    def __call__(self, **kwargs):
        self._apply_publishable_redirection()
        return Cached.__call__(self, **kwargs)

    @request_property
    def response_uses_cache(self):
        return (
            Cached.response_uses_cache(self)
            and app.publishable
            and app.publishable.cacheable
            and app.error is None
            and self.caching_policy
            and self.caching_policy.cache_enabled
        )

    @request_property
    def response_uses_server_side_cache(self):
        return (
            Cached.response_uses_server_side_cache(self)
            and self.caching_policy.server_side_cache
            and (
                app.publishable
                and app.publishable.cacheable_server_side
            )
        )

    @request_property
    def caching_policy(self):
        return app.publishable.get_effective_caching_policy(
            **self.caching_context
        )

    @request_property
    def cache_key(self):
        return repr(
            self.caching_policy.get_content_cache_key(
                app.publishable,
                **self.caching_context
            )
        )

    @request_property
    def invalidation(self):
        invalidation = self.view or Cached.invalidation(self)
        invalidation.update_cache_expiration(
            self.caching_policy.get_content_expiration(
                app.publishable,
                base = invalidation.cache_expiration,
                **self.caching_context
            )
        )
        invalidation.cache_tags.update(
            self.caching_policy.get_content_tags(
                app.publishable,
                base = invalidation.cache_tags,
                **self.caching_context
            )
        )
        return invalidation

    def _produce_content(self, **kwargs):

        # Override the active theme
        theme = self.get_theme()
        if theme:
            app.theme = theme

        return BaseCMSController.__call__(self, **kwargs)

    def get_theme(self):

        theme = app.publishable.theme
        if theme:
            return theme

        template = self.get_template()
        return template and template.theme

    def get_template(self):
        return app.publishable.get_template()

    def _render_template(self):
        if not self.view:
            raise cherrypy.NotFound()
        return BaseCMSController._render_template(self)

    def _apply_publishable_redirection(self):

        publishable = app.publishable

        if publishable.redirection_mode:

            redirection_target = publishable.find_redirection_target()

            if redirection_target is None:
                raise cherrypy.NotFound()

            if redirection_target.is_internal_content():
                parameters = get_request_url().query.fields
            else:
                parameters = None

            uri = redirection_target.get_uri(parameters = parameters)
            method = publishable.redirection_method

            if method == "perm":
                redirect(uri, status = 301)
            elif method == "client":
                return """
                    <!DOCTYPE html>
                    <html lang="%s">
                        <head>
                            <meta http-equiv="Content-Type" content="text/html;charset=utf-8"/>
                            <meta http-equiv="refresh" content="1; url=%s"/>
                            <title>%s</title>
                        </head>
                        <body>
                            %s
                            <script type="text/javascript">
                                location.href = publishable.getElementById("woost-client-redirection").href;
                            </script>
                        </body>
                    </html>
                """ % (
                    get_language(),
                    uri,
                    translations("woost.controllers.publishablecontroller.redirection_title"),
                    translations(
                        "woost.controllers.publishablecontroller.redirection_explanation",
                        uri = uri
                    )
                )
            else:
                redirect(uri)

