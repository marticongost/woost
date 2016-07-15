#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from cocktail.stringutils import normalize
from cocktail.translations import translations, get_language, require_language
from cocktail.urls import URL, URLBuilder
from cocktail.controllers import get_request_url
from woost import app
from woost.models import Configuration, Publishable
from woost.models.utils import get_matching_website

NO_MATCH = 0
IGNORED = 1
MATCH = 2


class URLMapping(object):

    def __init__(self, schemes = None):
        self.schemes = [] if schemes is None else schemes

    def get_url(
        self,
        publishable = None,
        language = None,
        website = None,
        host = "?",
        path = None,
        parameters = None,
        **kwargs
    ):
        # Language
        if not language:
            if publishable and publishable.per_language_publication:
                language = require_language()
            else:
                language = get_language()

        # Website
        if website is None:
            if publishable:
                website = get_matching_website(publishable)
            else:
                website = Configuration.instance.websites[0]

        # HTTPS policy
        scheme = None
        if website:
            https_policy = website.https_policy
            if (
                https_policy == "always"
                or (
                    https_policy == "per_page" and (
                        (publishable and publishable.requires_https)
                        or (app.user and not app.user.anonymous)
                    )
                )
            ):
                scheme = "https"

        # Custom hostname
        hostname = host if host not in ("!", "?") else None

        # Composition
        for url_scheme in self.schemes:

            url_builder = URLBuilder(
                scheme = scheme,
                hostname = hostname
            )

            result = url_scheme.build_url(
                url_builder,
                publishable = publishable,
                language = language,
                website = website,
                host = host,
                **kwargs
            )

            if result != NO_MATCH:

                if path:
                    url_builder.path.extend(path)

                if parameters:
                    url_builder.query.update(parameters)

                return url_builder.get_url()

        return None

    def resolve(self, url):

        url = URL(url)

        for scheme in self.schemes:
            resolution = URLResolution(url.path.segments)
            result = scheme.resolve(url, resolution)
            if result != NO_MATCH:
                return resolution

        return None

    def transform_request_url(self, **context):

        url = get_request_url()
        url_resolution = app.url_resolution

        if not url_resolution:
            url_resolution = self.resolve(url)
            if url_resolution is None:
                raise ValueError("Can't resolve %s" % url)

        context.setdefault("website", app.website)
        context.setdefault("language", get_language())
        context.setdefault("publishable", app.publishable)

        translation_url = self.get_url(**context)

        # Preserve extra path / query string parameters
        if translation_url and (
            url_resolution.remaining_segments
            or url.query
        ):
            translation_url = translation_url.copy(
                path = translation_url.path.append(
                    url_resolution.remaining_segments
                ),
                query = url.query.merge(translation_url.query)
            )

        return translation_url

    def get_canonical_url(
        self,
        url,
        url_resolution = None,
        **kwargs
    ):
        if url_resolution is None:
            url_resolution = self.resolve(url)

        if url_resolution is None or url_resolution.website is None:
            return url

        kwargs.setdefault("publishable", url_resolution.publishable)
        kwargs.setdefault("website", url_resolution.website)
        kwargs.setdefault("language", url_resolution.language)
        kwargs.setdefault("host", "!")

        canonical_url = app.url_mapping.get_url(**kwargs)

        if (
            canonical_url.scheme != url.scheme
            or canonical_url.hostname != url.hostname
            or canonical_url.port != url.port
            or canonical_url.path.segments
               != tuple(url_resolution.consumed_segments)
            or any(
                value != url.query.fields[key]
                for key, value in canonical_url.query.fields.iteritems()
            )
        ):
            return canonical_url.copy(
                path = canonical_url.path.append(
                    url_resolution.remaining_segments
                ),
                query = url.query.merge(canonical_url.query)
            )

        return url


class URLComponent(object):

    def build_url(
        self,
        url_builder,
        **kwargs
    ):
        raise TypeError(
            "%r doesn't implement its apply() method"
            % self.__class__
        )

    def resolve(self, url, resolution):
        raise TypeError(
            "%r doesn't implement its resolve() method"
            % self.__class__
        )


class URLResolution(object):
    publishable = None
    website = None
    language = None

    def __init__(self, path_segments):
        self.__consumed_segments = []
        self.__remaining_segments = list(path_segments)

    @property
    def consumed_segments(self):
        return self.__consumed_segments

    @property
    def remaining_segments(self):
        return self.__remaining_segments

    def consume_segment(self):
        self.__consumed_segments.append(self.__remaining_segments.pop(0))


class Sequence(URLComponent):

    def __init__(self, components = None):
        URLComponent.__init__(self)
        self.components = [] if components is None else components

    def build_url(
        self,
        url_builder,
        **kwargs
    ):
        sequence_result = NO_MATCH

        for component in self.components:
            result = component.build_url(
                url_builder,
                **kwargs
            )
            if result == NO_MATCH:
                return result
            else:
                sequence_result = max(sequence_result, result)

        return sequence_result

    def resolve(self, url, resolution):

        sequence_result = NO_MATCH

        for component in self.components:
            result = component.resolve(url, resolution)
            if result == NO_MATCH:
                return result
            else:
                sequence_result = max(sequence_result, result)

        return sequence_result


class OneOf(URLComponent):

    def __init__(self, components):
        URLComponent.__init__(self)
        self.components = components

    def build_url(
        self,
        url_builder,
        **kwargs
    ):
        for component in self.components:
            result = component.build_url(
                url_builder,
                **kwargs
            )
            if result == MATCH:
                return result

        return NO_MATCH

    def resolve(self, url, resolution):

        for component in self.components:
            result = component.resolve(url, resolution)
            if result == MATCH:
                return result

        return NO_MATCH


class Optional(URLComponent):

    def __init__(self, component):
        URLComponent.__init__(self)
        self.component = component

    def build_url(
        self,
        url_builder,
        **kwargs
    ):
        result = self.component.build_url(
            url_builder,
            **kwargs
        )

        if result == NO_MATCH:
            return IGNORED
        else:
            return result

    def resolve(self, url, resolution):

        result = self.component.resolve(url, resolution)

        if result == NO_MATCH:
            return IGNORED
        else:
            return result


class WebsiteInHostname(URLComponent):

    def build_url(
        self,
        url_builder,
        website = None,
        host = None,
        **kwargs
    ):
        if website and (
            host == "!"
            or (host == "?" and website is not app.website)
        ):
            url_builder.hostname = website.hosts[0]
            return MATCH
        else:
            return IGNORED

    def resolve(self, url, resolution):

        if url.hostname:
            website = Configuration.instance.get_website_by_host(url.hostname)
            if website:
                resolution.website = website
                return MATCH

        return NO_MATCH


class LocaleInPath(URLComponent):

    def build_url(
        self,
        url_builder,
        publishable = None,
        language = None,
        **kwargs
    ):
        if publishable and publishable.per_language_publication:
            code = self.get_code_for_locale(language)
            if code:
                url_builder.path.append(code)
                return MATCH
            else:
                return NO_MATCH
        else:
            return IGNORED

    def resolve(self, url, resolution):

        if resolution.remaining_segments:
            code = resolution.remaining_segments[0]
            locale = self.get_locale_from_code(code)
            if locale and locale in Configuration.instance.languages:
                resolution.language = locale
                resolution.consume_segment()
                return MATCH

        return NO_MATCH

    def get_code_for_locale(self, locale):
        return locale

    def get_locale_from_code(self, code):
        return code


class PathLiteral(URLComponent):

    literal = None

    def __init__(self, literal):
        URLComponent.__init__(self)
        self.literal = literal

    def build_url(
        self,
        url_builder,
        **kwargs
    ):
        url_builder.path.append(self.literal)
        return MATCH

    def resolve(self, url, resolution):
        if (
            resolution.remaining_segments
            and resolution.remaining_segments[0] == self.literal
        ):
            resolution.consume_segment()
            return MATCH
        else:
            return NO_MATCH


class Home(URLComponent):

    def build_url(
        self,
        url_builder,
        publishable = None,
        **kwargs
    ):
        if publishable:
            for website in Configuration.instance.websites:
                if publishable is website.home:
                    return MATCH

        return NO_MATCH

    def resolve(self, url, resolution):

        if not resolution.remaining_segments:
            website = resolution.website or app.website
            if website:
                resolution.publishable = website.home
                return MATCH

        return NO_MATCH


class IdInPath(URLComponent):

    include_file_extensions = True

    def build_url(
        self,
        url_builder,
        publishable = None,
        **kwargs
    ):
        if publishable:
            string = str(publishable.id)

            if self.include_file_extensions:
                file_ext = self.get_file_extension(publishable)
                if file_ext:
                    string += file_ext

            url_builder.path.append(string)
            return MATCH
        else:
            return NO_MATCH

    def resolve(self, url, resolution):

        if resolution.remaining_segments:

            id_string = resolution.remaining_segments[0]
            if self.include_file_extensions:
                id_string = strip_extension(id_string)

            try:
                id = int(id_string)
            except ValueError:
                pass
            else:
                publishable = Publishable.get_instance(id)
                if publishable:
                    resolution.publishable = publishable
                    resolution.consume_segment()
                    return MATCH

        return NO_MATCH

    def get_file_extension(self, publishable):
        return getattr(publishable, "file_extension", None)


class DescriptiveIdInPath(URLComponent):

    id_separator = "_"
    word_separator = "-"
    title_splitter_regexp = re.compile(r"\W+", re.UNICODE)
    normalized = True
    include_file_extensions = True

    def build_url(
        self,
        url_builder,
        publishable = None,
        language = None,
        **kwargs
    ):
        if publishable:
            title = self.get_title(publishable, language)

            if title:
                string = u"%s%s%d" % (title, self.id_separator, publishable.id)
            else:
                string = str(publishable.id)

            if self.include_file_extensions:
                file_ext = self.get_file_extension(publishable)
                if file_ext:
                    string += file_ext

            url_builder.path.append(string)
            return MATCH
        else:
            return NO_MATCH

    def resolve(self, url, resolution):

        if resolution.remaining_segments:

            parts = (
                resolution.remaining_segments[0]
                .rsplit(self.id_separator, 1)
            )

            if len(parts) == 1:
                id_string = parts[0]
            elif len(parts) == 2:
                id_string = parts[1]
            else:
                id_string = None

            if id_string:
                if self.include_file_extensions:
                    id_string = strip_extension(id_string)
                try:
                    id = int(id_string)
                except ValueError:
                    pass
                else:
                    publishable = Publishable.get_instance(id)
                    if publishable:
                        resolution.publishable = publishable
                        resolution.consume_segment()
                        return MATCH

        return NO_MATCH

    def get_title(self, publishable, language):

        title = translations(
            publishable,
            language,
            discard_generic_translation = True
        )

        if title:

            if self.normalized:
                title = normalize(title)

            title = self.title_splitter_regexp.sub(
                self.word_separator,
                title
            )

        return title

    def get_file_extension(self, publishable):
        return getattr(publishable, "file_extension", None)


class HierarchyInPath(URLComponent):

    def build_url(
        self,
        url_builder,
        publishable = None,
        language = None,
        **kwargs
    ):
        if publishable:
            path = self.get_path(publishable, **kwargs)

            if path:
                url_builder.path.extend(path.split("/"))
                return MATCH
            else:
                return IGNORED
        else:
            return NO_MATCH

    def resolve(self, url, resolution):

        path = list(resolution.remaining_segments)

        while path:
            publishable = Publishable.get_instance(full_path = u"/".join(path))
            if publishable:
                resolution.publishable = publishable
                for segment in path:
                    resolution.consume_segment()
                return MATCH
            else:
                path.pop(-1)

        return NO_MATCH

    def get_path(self, publishable, **kwargs):
        return publishable.full_path

def strip_extension(string):
    pos = string.find(".")
    if pos != -1:
        string = string[:pos]
    return string

