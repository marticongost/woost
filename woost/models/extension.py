#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import pkgutil
import importlib
import os.path
from threading import RLock
from cocktail.events import Event
from cocktail.translations import translations
from cocktail.ui import components
from cocktail.persistence import (
    datastore,
    transaction,
    PersistentSet
)
from woost import app
from woost import extensions as ext_root
from .configuration import Configuration


class ExtensionsManager(object):

    extension_loaded = Event()

    def __init__(self):
        self.__extensions_lock = RLock()
        self.__loaded_extensions = set()

    def iter_extensions(self):
        """Find all available extensions.

        Woost extensions are implemented as subpackages of the woost.extensions
        namespace package.

        :return: An iterable sequence of packages.
        """
        for finder, name, ispkg in pkgutil.iter_modules(
            ext_root.__path__,
            ext_root.__name__ + "."
        ):
            yield importlib.import_module(name)

    def load_extensions(self):
        """Load all available extensions.

        This is tipically called during application start up, and follows this
        sequence:

            * Extensions are discovered by invoking `iter_extensions()`
            * Each extension is initialized, in order, by passing it to
              the `load_extension()` function
        """
        for extension in self.iter_extensions():
            self.load_extension(extension)

    def load_extension(self, extension):
        """Initializes the given extension.

        If the extension package defines an 'install()' function, and it is the
        first time that the extension is initialized, it will be called as a
        datastore transaction. This gives the extension a chance to create its
        required assets.

        If the extension package defines a 'load()' function at its root, it will
        be called.

        It is safe to call this function on the same extension multiple times;
        subsequent calls will become a no-op.

        :param extension: An extension package.

        :return: True if the extension had not been loaded yet and has been
            initialized; False otherwise.
        """
        if extension in self.__loaded_extensions:
            return False

        with self.__extensions_lock:

            if extension in self.__loaded_extensions:
                return False

            self._define_resource_repositories(extension)

            install_ext = getattr(extension, "install", None)
            if install_ext:

                def installation():
                    KEY = "woost.installed_extensions"
                    try:
                        installed_extensions = datastore.root[KEY]
                    except KeyError:
                        installed_extensions = PersistentSet()
                        datastore.root[KEY] = installed_extensions
                    install_ext()
                    installed_extensions.add(extension.__name__)

                transaction(installation)

            load_ext = getattr(extension, "load", None)
            if load_ext:
                load_ext()

            self.extension_loaded(extension = extension)
            self.__loaded_extensions.add(extension)

        return True

    def _define_resource_repositories(self, extension):

        ext_path = os.path.dirname(extension.__file__)

        # - woost.extensions.EXTENSION
        resources_path = os.path.join(ext_path, "resources")
        repo_name = extension.__name__

        if os.path.exists(resources_path):
            app.add_resources_repository(repo_name, resources_path)

            # Icon repository
            icon_path = os.path.join(resources_path, "images", "icons")

            if os.path.exists(icon_path):
                icon_url = "%s://images/icons" % repo_name
                app.icon_resolver.icon_repositories.insert(0, (
                    icon_path,
                    icon_url
                ))

        # - woost.extensions.EXTENSION.admin.ui
        admin_resources_path = os.path.join(
            ext_path,
            "admin", "ui", "resources"
        )

        if os.path.exists(admin_resources_path):
            admin_repo_name = repo_name + ".admin.ui"
            app.add_resources_repository(
                admin_repo_name,
                admin_resources_path
            )
            components.theme.add_location(admin_repo_name + "://styles")


extensions_manager = ExtensionsManager()


class ExtensionAssets:
    """Convenience class for creating content when installing an extension."""

    TRANSLATIONS = object()

    def __init__(self, extension_name):
        self.extension_name = extension_name

    def new(self, cls, asset_name, **kwargs):
        asset = cls()
        asset.qname = qname = "woost.extensions.%s.%s" % (
            self.extension_name,
            asset_name
        )

        if kwargs:
            for key, value in kwargs.items():
                if value is self.TRANSLATIONS:
                    for language in Configuration.instance.languages:
                        value = translations(qname + "." + key, language)
                        if value:
                            asset.set(key, value, language)
                else:
                    asset.set(key, value)

        asset.insert()
        return asset

# Required for backwards compatibility
load_extensions = extensions_manager.load_extensions

