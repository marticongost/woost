#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from types import ModuleType
import sys
import os
from threading import local
from pkg_resources import resource_filename
from cocktail.modeling import GenericMethod, camel_to_underscore
from cocktail.caching import Cache
from cocktail.controllers import context, folder_publisher, Cached
from cocktail.controllers.asyncupload import AsyncUploader
from cocktail.html.resources import resource_repositories, get_theme, set_theme


class Application(ModuleType):
    """Provides configuration and contextual state for a Woost application."""

    _contextual_properties = []

    __package = None
    __root = None
    __icon_resolver = None
    __custom_icon_repository = None

    __language = None
    __authentication = None

    installation_id = None
    installation_color = None

    splash = """\
Made with                     _
__        __ ___   ___   ___ | |_
\ \  __  / // _ \ / _ \ / __||  _|
 \ \/  \/ /| (_) | (_) |___ \| |__
  \__/\__/  \___/ \___/|____/\___/

http://woost.info
"""

    default_remote_host = None
    default_remote_python_executable = None

    def __init__(self):
        ModuleType.__init__(self, "woost.app", self.__doc__)
        self._thread_data = local()

    def path(self, *args):
        return os.path.join(self.root, *args)

    def _get_package(self):
        return self.__package

    def _set_package(self, package):
        self.__package = package
        self.__add_custom_icon_repository()

    package = property(_get_package, _set_package)

    def _get_root(self):
        if self.__root is None and self.__package:
            return resource_filename(self.__package, "")

        return self.__root

    def _set_root(self, root):
        self.__root = root
        self.__add_custom_icon_repository()

    root = property(_get_root, _set_root)

    def __add_custom_icon_repository(self):

        root = self.root
        package = self.package

        if root and package:

            repository_uri = resource_repositories.normalize_uri(
                "%s://images/icons" % package
            )

            if repository_uri:
                repository = (
                    self.path("views", "resources", "images", "icons"),
                    repository_uri
                )

                if (
                    self.__custom_icon_repository is not None
                    and self.__custom_icon_repository != repository
                ):
                    self.icon_resolver.icon_repositories.remove(
                        self.__custom_icon_repository
                    )

                self.__custom_icon_repository = repository
                self.icon_resolver.icon_repositories.insert(0, repository)

    @property
    def icon_resolver(self):
        if self.__icon_resolver is None:
            from woost.icons import IconResolver
            self.__icon_resolver = IconResolver()
        return self.__icon_resolver

    def ascend_navigation(self):
        pub = self.publishable
        nav_point = self.navigation_point
        if pub is nav_point:
            for pub in pub.ascend_tree(include_self = True):
                yield pub
        else:
            yield pub
            for pub in nav_point.ascend_tree(include_self = True):
                yield pub

    # Language scheme
    def _get_language(self):
        if self.__language is None:
            from woost.language import LanguageScheme
            self.__language = LanguageScheme()
        return self.__language

    def _set_language(self, language):
        self.__language = language

    language = property(_get_language, _set_language)

    # Authentication scheme
    def _get_authentication(self):
        if self.__authentication is None:
            from woost.authentication import AuthenticationScheme
            self.__authentication = AuthenticationScheme()
        return self.__authentication

    def _set_authentication(self, authentication):
        self.__authentication = authentication

    authentication = property(_get_authentication, _set_authentication)

    # Caching
    cache = Cache()

    # URLs
    __url_mapping = None

    def _get_url_mapping(self):

        if self.__url_mapping is None:
            from woost import urls
            url_mapping = urls.URLMapping([
                urls.Sequence([
                    urls.Optional(urls.WebsiteInHostname()),
                    urls.Optional(urls.LocaleInPath()),
                    urls.Conditional(
                        (
                            lambda publishable, **kwargs:
                            publishable is not None
                        ),
                        urls.OneOf([
                            urls.Home(),
                            urls.HierarchyInPath(),
                            urls.DescriptiveIdInPath(),
                            urls.IdInPath()
                        ])
                    )
                ])
            ])
            self.__url_mapping = url_mapping

        return self.__url_mapping

    def _set_url_mapping(self, url_mapping):
        self.__url_mapping = url_mapping

    url_mapping = property(_get_url_mapping, _set_url_mapping)

    # Asynchronous file uploads
    async_uploader = AsyncUploader()
    async_uploader.session_prefix = "woost.async_upload."

    # Tracebacks
    traceback_link_style = "disabled"

    # Context
    def clear_context(self):
        for prop in self._contextual_properties:
            setattr(self, prop.attr, None)

    def add_resources_repository(self, repository_name, repository_path):
        from woost.controllers.cmsresourcescontroller import CMSResourcesController
        resource_repositories.define(
            repository_name,
            "/resources/" + repository_name,
            repository_path
        )
        setattr(
            CMSResourcesController,
            repository_name.replace(".", "_"),
            folder_publisher(repository_path)
        )
        if repository_name == self.package:
            self.__add_custom_icon_repository()


ContextualProperty = None

class ContextualPropertyMetaclass(type):

    def __init__(cls, name, bases, members):
        type.__init__(cls, name, bases, members)

        # Automaticall register subclasses
        if ContextualProperty:
            NAME_SUFFIX = "Property"
            if name.endswith(NAME_SUFFIX):
                cls.attr = camel_to_underscore(name[:-len(NAME_SUFFIX)])
                prop = cls()
                setattr(Application, cls.attr, prop)
                Application._contextual_properties.append(prop)


class ContextualProperty(metaclass = ContextualPropertyMetaclass):

    default = None

    def __get__(self, instance, cls = None):
        if instance is None:
            return self
        else:
            return self.get(instance)

    def __set__(self, instance, value):
        self.set(instance, value)

    def get(self, app):
        return getattr(app._thread_data, self.attr, self.default)

    def set(self, app, value):
        setattr(app._thread_data, self.attr, value)


class URLResolutionProperty(ContextualProperty):
    """Gets or sets the URL resolution for the current request.

    .. type:: `~woost.urls.URLResolution`
    """


class ErrorProperty(ContextualProperty):
    """Gets or sets the last error for the current context.

    "Context" is typically an HTTP request, but the property can also be
    used outside a web request/response cycle.

    .. type:: Exception
    """


class TracebackProperty(ContextualProperty):
    """Gets or sets the last traceback for the current context.

    "Context" is typically an HTTP request, but the property can also be
    used outside a web request/response cycle.

    .. type:: Traceback
    """


class UserProperty(ContextualProperty):
    """Gets or sets the active user for the current context.

    "Context" is typically an HTTP request, but the property can also be
    used outside a web request/response cycle.

    .. type:: `woost.models.User`
    """


class WebsiteProperty(ContextualProperty):
    """Gets or sets the active website for the current context.

    "Context" is typically an HTTP request, but the property can also be
    used outside a web request/response cycle.

    .. type:: `woost.models.Website`
    """


class PublishableProperty(ContextualProperty):
    """Gets or sets the active publishable for the current context.

    "Context" is typically an HTTP request, but the property can also be
    used outside a web request/response cycle.

    .. type:: `woost.models.PublishableObject`
    """

    def set(self, app, value):

        ContextualProperty.set(self, app, value)

        if app.original_publishable is None:
            app.navigation_point = get_navigation_point(value)

        # Required to preserve backward compatibility
        context["publishable"] = value


class OriginalPublishableProperty(ContextualProperty):
    """Gets or sets the active original_publishable for the current context.

    "Context" is typically an HTTP request, but the property can also be
    used outside a web request/response cycle.

    .. type:: `woost.models.original_publishable`
    """

    def set(self, app, value):
        ContextualProperty.set(self, app, value)
        app.navigation_point = get_navigation_point(value)

        # Required to preserve backward compatibility
        context["original_publishable"] = value


class NavigationPointProperty(ContextualProperty):
    """Gets or sets the active navigation point for the current context.

    The navigation point is the publishable that should be highlighted as
    the active element in the navigation controls of the site's user
    interface. This will usually be the same as the active publishable,
    but not always: news items are a typical use case where the active
    publishable (the piece of news) and the highlighted page (the news
    listing) will differ.

    "Context" is typically an HTTP request, but the property can also be
    used outside a web request/response cycle.

    .. type:: `woost.models.PublishableObject`
    """


class ThemeProperty(ContextualProperty):
    """Gets or sets the active theme for the current context.

    "Context" is typically an HTTP request, but the property can also be
    used outside a web request/response cycle.

    .. type:: `woost.models.Theme`
    """

    def set(self, app, value):
        ContextualProperty.set(self, app, value)
        set_theme(value and value.identifier or None)


class EditingProperty(ContextualProperty):
    """Indicates wether the active publishable is being served in the context
    of an edit session.

    This can be used by controllers and templates to temporarily change the
    state for the publishable to reflect the current edit session, or to
    toggle the visibility of inline editing aids.

    "Context" is typically an HTTP request, but the property can also be
    used outside a web request/response cycle.

    .. type:: bool
    """
    default = False


@GenericMethod
def get_navigation_point(self):
    return self


Cached.cache = Application.cache

sys.modules["woost.app"] = Application()

