#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from __future__ import with_statement
from types import GeneratorType
from threading import Lock
from time import time, mktime
from datetime import datetime
from hashlib import md5
import cherrypy
from cherrypy.lib import cptools, http
from cocktail.caching import CacheKeyError
from woost import app
from woost.controllers import BaseCMSController


class PublishableController(BaseCMSController):
    """Base controller for all publishable items (documents, files, etc)."""

    cache_enabled = True

    cached_headers = (
        "Content-Type",
        "Content-Length",
        "Content-Disposition",
        "Content-Encoding",
        "Last-Modified",
        "ETag"
    )

    def __call__(self, **kwargs):

        cherrypy.response.headers["Cache-Control"] = "no-cache"
        content = self._apply_cache(**kwargs)

        if content is None:
            content = self._produce_content(**kwargs)

        return content

    def _apply_cache(self, **kwargs):

        publishable = app.publishable
        request = cherrypy.request
        response = cherrypy.response
        response_headers = response.headers

        # Make sure caching is enabled
        if not (
            self.cache_enabled
            and app.cache.enabled
            and app.cache.storage
            and publishable.cacheable
            and request.method == "GET"
            and app.error is None
        ):
            return None

        # Get the caching policy for the active request
        caching_context = {
            "request": request,
            "controller": self
        }

        policy = publishable.get_effective_caching_policy(**caching_context)

        if policy is None or not policy.cache_enabled:
            return None

        server_side_cache = (
            policy.server_side_cache
            and publishable.cacheable_server_side
        )

        # Find the unique cache identifier for the requested content
        cache_key = repr(policy.get_content_cache_key(
            publishable,
            **caching_context
        ))

        # Look for a cached response
        try:
            content, headers, gen_time = app.cache.retrieve(cache_key)
        except CacheKeyError:
            content = None
            headers = None
            gen_time = time()
        else:
            if server_side_cache:
                if headers:
                    response_headers.update(headers)
            else:
                # Server-side caching disabled, we only care about generation
                # time to valide the ETag
                content = None
                headers = None

        response_headers["ETag"] = str(gen_time)

        if not server_side_cache:
            cptools.validate_etags()

        if content is None:
            content = self.__produce_response(**kwargs)

            view = self.view
            cache_entry_expiration = policy.get_content_expiration(
                publishable,
                base = view and view.cache_expiration,
                **caching_context
            )
            cache_entry_tags = policy.get_content_tags(
                publishable,
                base = view and view.cache_tags,
                **caching_context
            )

            # Store content in the server side cache
            if server_side_cache:

                cache_entry_content = content

                # Collect headers that should be included in the cache
                cache_entry_headers = {}

                for header_name in self.cached_headers:
                    header_value = response_headers.get(header_name)
                    if header_value:
                        cache_entry_headers[header_name] = header_value
            else:
                cache_entry_headers = None
                cache_entry_content = None

            # Store the response in the cache
            app.cache.store(
                cache_key,
                (cache_entry_content, cache_entry_headers, gen_time),
                expiration = cache_entry_expiration,
                tags = cache_entry_tags
            )

        if server_side_cache:
            cptools.validate_etags()

        return content

    def __produce_response(self, **kwargs):
        content = self._produce_content(**kwargs)

        if isinstance(content, GeneratorType):
            content_bytes = "".join(
                chunk.encode("utf-8")
                    if isinstance(chunk, unicode)
                    else chunk
                for chunk in content
            )
        elif isinstance(content, unicode):
            content_bytes = content.encode("utf-8")
        else:
            content_bytes = content

        return content_bytes

    def _produce_content(self, **kwargs):
        return BaseCMSController.__call__(self, **kwargs)

