#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import pkgutil
import importlib
from threading import RLock
from cocktail.events import Event
from woost import extensions as ext_root


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

            load_ext = getattr(extension, "load", None)
            if load_ext:
                load_ext()

            self.extension_loaded(extension = extension)
            self.__loaded_extensions.add(extension)

        return True


extensions_manager = ExtensionsManager()

# Required for backwards compatibility
load_extensions = extensions_manager.load_extensions

