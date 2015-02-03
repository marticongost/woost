#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import os
from pkg_resources import resource_filename


class Application(object):

    __root = None
    __icon_resolver = None

    __language = None
    __authentication = None

    installation_id = None
    installation_color = None

    def path(self, *args):
        return os.path.join(self.root, *args)

    def _get_package(self):
        return self.__package

    def _set_package(self, package):
        self.__package = package
        self.root = resource_filename(package, "")

    package = property(_get_package, _set_package)

    def _get_root(self):
        return self.__root

    def _set_root(self, root):

        if self.__root:
            old_path = self.path("views", "resources", "images", "icons")
            for path, url in self.icon_resolver.icon_repositories:
                if path == old_path:
                    self.icon_resolver.icon_repositories.remove((path, url))

        self.__root = root

        if root:
            # Add an application specific icon repository
            self.icon_resolver.icon_repositories.insert(
                0, (self.path("views", "resources", "images", "icons"),
                    "/" + self.package + "_resources/images/icons")
            )

    root = property(_get_root, _set_root)

    @property
    def icon_resolver(self):
        if self.__icon_resolver is None:
            from woost.iconresolver import IconResolver
            self.__icon_resolver = IconResolver()
        return self.__icon_resolver

    # Language scheme
    __language = None

    def _get_language(self):
        if self.__language is None:
            from woost.languagescheme import LanguageScheme
            self.__language = LanguageScheme()
        return self.__language

    def _set_language(self, language):
        self.__language = language

    language = property(_get_language, _set_language)

    # Authentication scheme
    __authentication = None

    def _get_authentication(self):
        if self.__authentication is None:
            from woost.authenticationscheme import AuthenticationScheme
            self.__authentication = AuthenticationScheme()
        return self.__authentication

    def _set_authentication(self, authentication):
        self.__authentication = authentication

    authentication = property(_get_authentication, _set_authentication)

