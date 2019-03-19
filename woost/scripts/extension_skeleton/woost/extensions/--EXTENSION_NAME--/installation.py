--MODULE_HEADER--
from woost.models import ExtensionAssets


def install():
    """Creates the assets required by the --EXTENSION_NAME-- extension."""

    assets = ExtensionAssets("--EXTENSION_NAME--")

