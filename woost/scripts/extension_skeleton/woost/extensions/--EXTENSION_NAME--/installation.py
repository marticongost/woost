"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from woost.models import ExtensionAssets

translations.load_bundle("woost.extensions.--EXTENSION_NAME--.installation")

assets = ExtensionAssets("--EXTENSION_NAME--")

def install():
    """Creates the assets required by the --EXTENSION_NAME-- extension."""

