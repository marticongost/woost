"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from typing import (
    Callable,
    Mapping,
    Optional as Opt,
    Pattern,
    Sequence,
    Set,
    Type
)
import re

from cocktail.stringutils import normalize
from cocktail.translations import translations, get_language, require_language
from cocktail.urls import URL, URLBuilder
from cocktail.controllers import get_request_url

from woost import app
from woost.models import (
    Configuration,
    Website,
    Item,
    PublishableObject,
    get_publishable,
    get_publishable_by_full_path
)
from woost.models.utils import get_matching_website

NO_MATCH = 0
IGNORED = 1
MATCH = 2

component_result = int


class URLMapping:

    def __init__(self, schemes: Sequence["URLComponent"] = None):
        self.schemes = [] if schemes is None else schemes

    def get_url(
        self,
        publishable: PublishableObject = None,
        language: str = None,
        website: Website = None,
        scheme: str = None,
        host: str = "?",
        path: Sequence[str] = None,
        parameters: Mapping[str, str] = None,
        **kwargs) -> URL:

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
                website = Website.select()[0]

        # HTTPS policy
        if scheme is None and website:
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
        if host == ".":
            hostname = get_request_url().hostname
        else:
            hostname = host if host not in ("!", "?") else None

        # Composition
        for url_scheme in self.schemes:

            url_builder = URLBuilder(scheme=scheme, hostname=hostname)

            result = url_scheme.build_url(
                url_builder,
                publishable=publishable,
                language=language,
                website=website,
                host=host,
                scheme=scheme,
                **kwargs
            )

            if result != NO_MATCH:

                if path:
                    url_builder.path.extend(path)

                if parameters:
                    url_builder.query.update(parameters)

                return url_builder.get_url()

        return None

    def resolve(self, url: URL) -> Opt["URLResolution"]:

        url = URL(url)

        for scheme in self.schemes:
            resolution = URLResolution(url.path.segments)
            result = scheme.resolve(url, resolution)
            if result != NO_MATCH:
                return resolution

        return None

    def transform_request_url(self, **context) -> URL:

        url = get_request_url()
        url_resolution = app.url_resolution

        if not url_resolution:
            url_resolution = self.resolve(url)
            if url_resolution is None:
                raise ValueError(f"Can't resolve {url}")

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
                path=translation_url.path.append(
                    url_resolution.remaining_segments
                ),
                query=url.query.merge(translation_url.query)
            )

        return translation_url

    def get_canonical_url(
        self,
        url: URL,
        url_resolution: "URLResolution" = None,
        **kwargs) -> URL:

        if url_resolution is None:
            url_resolution = self.resolve(url)

        if url_resolution is None:
            return url

        kwargs.setdefault("publishable", url_resolution.publishable)
        kwargs.setdefault("website", url_resolution.website)
        kwargs.setdefault("language", url_resolution.language)
        kwargs.setdefault("host", "!")

        canonical_url = app.url_mapping.get_url(**kwargs)

        if url_resolution.canonical_parameters:
            params = {}

            for key in url_resolution.canonical_parameters:
                value = url.query.fields.get(key)
                if value is not None:
                    params[key] = value

            if params:
                canonical_url = canonical_url.merge_query(params)

        return canonical_url


class URLComponent:

    def build_url(
            self,
            url_builder: URLBuilder,
            **kwargs) -> component_result:

        raise TypeError(
            "%r doesn't implement its apply() method"
            % self.__class__
        )

    def resolve(
            self,
            url: URL,
            resolution: "URLResolution") -> component_result:

        raise TypeError(
            "%r doesn't implement its resolve() method"
            % self.__class__
        )


class URLResolution:
    publishable: PublishableObject = None
    website: Website = None
    language: str = None
    canonical_validation: bool = True
    canonical_parameters: Set[str] = None

    def __init__(self, path_segments: Sequence[str]):
        self.__consumed_segments = []
        self.__remaining_segments = list(path_segments)
        self.canonical_parameters = set()

    @property
    def consumed_segments(self) -> Sequence[str]:
        return self.__consumed_segments

    @property
    def remaining_segments(self) -> Sequence[str]:
        return self.__remaining_segments

    def consume_segment(self):
        self.__consumed_segments.append(self.__remaining_segments.pop(0))


class Sequence(URLComponent):

    def __init__(self, components: Sequence[URLComponent] = None):
        super().__init__()
        self.components = [] if components is None else components

    def build_url(
            self,
            url_builder: URLBuilder,
            **kwargs):

        sequence_result = NO_MATCH

        for component in self.components:
            result = component.build_url(url_builder, **kwargs)
            if result == NO_MATCH:
                return result
            else:
                sequence_result = max(sequence_result, result)

        return sequence_result

    def resolve(
            self,
            url: URL,
            resolution: "URLResolution") -> component_result:

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
        super().__init__()
        self.components = components

    def build_url(
            self,
            url_builder: URLBuilder,
            **kwargs) -> component_result:

        for component in self.components:
            result = component.build_url(
                url_builder,
                **kwargs
            )
            if result == MATCH:
                return result

        return NO_MATCH

    def resolve(
            self,
            url: URL,
            resolution: "URLResolution") -> component_result:

        for component in self.components:
            result = component.resolve(url, resolution)
            if result == MATCH:
                return result

        return NO_MATCH


class Optional(URLComponent):

    def __init__(self, component: URLComponent):
        super().__init__()
        self.component = component

    def build_url(
            self,
            url_builder: URLBuilder,
            **kwargs) -> component_result:

        result = self.component.build_url(url_builder, **kwargs)

        if result == NO_MATCH:
            return IGNORED
        else:
            return result

    def resolve(
            self,
            url: URL,
            resolution: "URLResolution") -> component_result:

        result = self.component.resolve(url, resolution)

        if result == NO_MATCH:
            return IGNORED
        else:
            return result


class Conditional(URLComponent):

    def __init__(
            self,
            condition: Callable[[], bool],
            component: URLComponent):

        super().__init__()
        self.condition = condition
        self.component = component

    def build_url(
            self,
            url_builder: URLBuilder,
            **kwargs) -> component_result:

        result = self.component.build_url(url_builder, **kwargs)

        if result == NO_MATCH:
            if self.condition(**kwargs):
                return NO_MATCH
            else:
                return IGNORED
        else:
            return result

    def resolve(
            self,
            url: URL,
            resolution: "URLResolution") -> component_result:

        result = self.component.resolve(url, resolution)

        if result == NO_MATCH:
            return IGNORED
        else:
            return result


class FixedHostname(URLComponent):

    hostname = None

    def __init__(self, hostname: str):
        super().__init__()
        self.hostname = hostname

    def build_url(
            self,
            url_builder: URLBuilder,
            host: str = None,
            **kwargs) -> component_result:

        if host == "!":
            url_builder.hostname = self.hostname
            return MATCH
        else:
            return IGNORED

    def resolve(
            self,
            url: URL,
            resolution: "URLResolution") -> component_result:

        if url.hostname == self.hostname:
            return MATCH
        else:
            return NO_MATCH


class WebsiteInHostname(URLComponent):

    def choose_hostname(self, website: Website) -> str:

        hosts = website.hosts

        if len(hosts) > 1:
            req_hostname = get_request_url().hostname
            if req_hostname in hosts:
                return req_hostname

        return hosts[0]

    def build_url(
            self,
            url_builder: URLBuilder,
            website: Website = None,
            host: str = None,
            scheme: str = None,
            **kwargs) -> component_result:

        if website and (
            host == "!"
            or (
                host == "?"
                and (website is not app.website or scheme == "https")
            )
            or (not host and scheme == "https")
        ):
            url_builder.hostname = self.choose_hostname(website)
            return MATCH
        else:
            return IGNORED

    def resolve(
            self,
            url: URL,
            resolution: "URLResolution") -> component_result:

        if url.hostname:
            website = Configuration.instance.get_website_by_host(url.hostname)
            if website:
                resolution.website = website
                return MATCH

        return NO_MATCH


class LocaleInPath(URLComponent):

    def build_url(
            self,
            url_builder: URLBuilder,
            publishable: PublishableObject = None,
            language: str = None,
            **kwargs) -> component_result:

        if publishable and publishable.per_language_publication:
            code = self.get_code_for_locale(language)
            if code:
                url_builder.path.append(code)
                return MATCH
            else:
                return NO_MATCH
        else:
            return IGNORED

    def resolve(
            self,
            url: URL,
            resolution: "URLResolution") -> component_result:

        if resolution.remaining_segments:
            code = resolution.remaining_segments[0]
            locale = self.get_locale_from_code(code)
            if locale and locale in Configuration.instance.languages:
                resolution.language = locale
                resolution.consume_segment()
                return MATCH

        return NO_MATCH

    def get_code_for_locale(self, locale: str) -> str:
        return locale

    def get_locale_from_code(self, code: str) -> str:
        return code


class PathLiteral(URLComponent):

    literal: str = None

    def __init__(self, literal: str):
        super().__init__()
        self.literal = literal

    def build_url(
            self,
            url_builder: URLBuilder,
            **kwargs) -> component_result:

        url_builder.path.append(self.literal)
        return MATCH

    def resolve(
            self,
            url: URL,
            resolution: "URLResolution") -> component_result:

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
            url_builder: URLBuilder,
            publishable: PublishableObject = None,
            **kwargs) -> component_result:

        if publishable:
            for website in Website.select():
                if publishable is website.home:
                    return MATCH

        return NO_MATCH

    def resolve(
            self,
            url: URL,
            resolution: "URLResolution") -> component_result:

        if not resolution.remaining_segments:
            website = resolution.website or app.website
            if website:
                resolution.publishable = website.home
                return MATCH

        return NO_MATCH


class IdInPath(URLComponent):

    prefix: str = None
    model: Type[Item] = None
    include_file_extensions: bool = True

    def __init__(
            self,
            prefix: str = None,
            model: Type[Item] = None,
            include_file_extensions: bool = True):

        super().__init__()
        self.prefix = prefix
        self.model = model
        self.include_file_extensions = include_file_extensions

    def build_url(
            self,
            url_builder: URLBuilder,
            publishable: PublishableObject = None,
            **kwargs) -> component_result:

        if (
            publishable
            and publishable.id
            and (
                self.model is None
                or isinstance(publishable, self.model)
            )
        ):
            if self.prefix:
                url_builder.path.append(self.prefix)

            string = str(publishable.id)

            if self.include_file_extensions:
                file_ext = self.get_file_extension(publishable)
                if file_ext:
                    string += file_ext

            url_builder.path.append(string)
            return MATCH
        else:
            return NO_MATCH

    def resolve(
            self,
            url: URL,
            resolution: "URLResolution") -> component_result:

        if (
            resolution.remaining_segments
            and (
                not self.prefix
                or (
                    len(resolution.remaining_segments) >= 2
                    and resolution.remaining_segments[0] == self.prefix
                )
            )
        ):
            id_index = 1 if self.prefix else 0
            id_string = resolution.remaining_segments[id_index]
            if self.include_file_extensions:
                id_string = strip_extension(id_string)

            try:
                id = int(id_string)
            except ValueError:
                pass
            else:
                publishable = get_publishable(id)
                if publishable and (
                    self.model is None
                    or isinstance(publishable, self.model)
                ):
                    resolution.publishable = publishable
                    if self.prefix:
                        resolution.consume_segment()
                    resolution.consume_segment()
                    return MATCH

        return NO_MATCH

    def get_file_extension(
            self,
            publishable: PublishableObject) -> Opt[str]:

        return getattr(publishable, "file_extension", None)


class DescriptiveIdInPath(URLComponent):

    id_separator: str = "_"
    word_separator: str = "-"
    title_splitter_regexp: Pattern = re.compile(r"\W+", re.UNICODE)
    normalized: bool = True
    include_file_extensions: bool = True
    allow_slashes_in_title: bool = False

    def applies_to_publishable(self, publishable: PublishableObject) -> bool:
        return True

    def build_url(
            self,
            url_builder: URLBuilder,
            publishable: PublishableObject = None,
            language: str = None,
            **kwargs) -> component_result:

        if publishable and self.applies_to_publishable(publishable):
            title = self.get_title(publishable, language)

            if title:
                string = "%s%s%d" % (title, self.id_separator, publishable.id)
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

    def resolve(
            self,
            url: URL,
            resolution: "URLResolution") -> component_result:

        if resolution.remaining_segments:

            for n, segment in enumerate(resolution.remaining_segments):

                if n > 0 and not self.allow_slashes_in_title:
                    break

                parts = segment.rsplit(self.id_separator, 1)

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
                        publishable = get_publishable(id)
                        if (
                            publishable
                            and self.applies_to_publishable(publishable)
                        ):
                            resolution.publishable = publishable
                            for _ in range(n + 1):
                                resolution.consume_segment()
                            return MATCH

        return NO_MATCH

    def get_title(self, publishable: PublishableObject, language: str) -> str:

        title = translations(
            publishable,
            language,
            discard_generic_translation=True
        )

        if title:
            title = self.escape_title(title)

        return title

    def escape_title(self, title: str) -> str:

        if self.normalized:
            title = normalize(title)

        title = self.title_splitter_regexp.sub(
            self.word_separator,
            title
        )

        return title

    def get_file_extension(
            self,
            publishable: PublishableObject) -> Opt[str]:

        return getattr(publishable, "file_extension", None)


class HierarchyInPath(URLComponent):

    def build_url(
            self,
            url_builder: URLBuilder,
            publishable: PublishableObject = None,
            language: str = None,
            **kwargs) -> component_result:

        if publishable:
            path = self.get_path(publishable, **kwargs)

            if path:
                url_builder.path.extend(path.split("/"))
                return MATCH
            else:
                return IGNORED
        else:
            return NO_MATCH

    def resolve(
            self,
            url: URL,
            resolution: "URLResolution") -> component_result:

        path = list(resolution.remaining_segments)

        while path:
            publishable = get_publishable_by_full_path( "/".join(path))
            if publishable:
                resolution.publishable = publishable
                for segment in path:
                    resolution.consume_segment()
                return MATCH
            else:
                path.pop(-1)

        return NO_MATCH

    def get_path(
            self,
            publishable: PublishableObject,
            **kwargs) -> Opt[str]:

        return publishable.full_path


def strip_extension(string: str) -> str:
    pos = string.find(".")
    if pos != -1:
        string = string[:pos]
    return string

