--MODULE_HEADER--
from cocktail import schema
from cocktail.translations import translations
from woost.models import add_setting

translations.load_bundle("woost.extensions.--EXTENSION_NAME--.settings")

