#-*- coding: utf-8 -*-
u"""Defines the `URLShortener` model.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import abstractmethod
from cocktail import schema
from cocktail.caching import Cache, CacheKeyError
from woost.models import Item


class URLShortener(Item):
    """Base model for all URL shortening services."""

    visible_from_root = False
    instantiable = False
    shourt_url_cache = Cache()

    title = schema.String(
        required = True,
        unique = True,
        indexed = True,
        normalized_index = True,
        descriptive = True
    )

    def request(self, url):

        short_url = None
        cache_key = (self.id, url)

        if short_url is None:
            try:
                short_url = short_url_cache.retrieve(url)
            except CacheKeyError:
                short_url = self.shorten_url(url)
                short_url_cache.store(cache_key, short_url)

        return short_url

    @abstractmethod
    def shorten_url(self, url):
        pass


class URLShortenerServiceError(Exception):
    """An exception raised if an error is reported during a request to an URL
    shortening service.
    """

    def __init__(self, response):
        Exception.__init__(self, response)
        self.response = response

