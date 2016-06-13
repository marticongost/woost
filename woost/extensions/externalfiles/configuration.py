#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from woost.models import Configuration

translations.load_bundle("woost.extensions.externalfiles.configuration")

Configuration.add_member(
    schema.String("external_files_host",
        text_search = False,
        member_group = "publication",
        listed_by_default = False
    )
)

