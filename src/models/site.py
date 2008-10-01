#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet.modeling import classgetter
from magicbullet import schema
from magicbullet.persistence import Entity, datastore


class Site(Entity):

    indexed = True

    @classgetter
    def main(cls):
        return datastore.root["main_site"]

    default_language = schema.String(
        required = True,
        default = "en"
    )
    
    languages = schema.Collection(
        required = True,
        min = 1,
        items = schema.String,
        default = ["en"]
    )

    home = schema.Reference(
        type = "magicbullet.models.Document",
        required = True
    )

    not_found_error_page = schema.Reference(
        type = "magicbullet.models.Document"
    )

    forbidden_error_page = schema.Reference(
        type = "magicbullet.models.Document"
    )
    
    generic_error_page = schema.Reference(
        type = "magicbullet.models.Document"
    )

