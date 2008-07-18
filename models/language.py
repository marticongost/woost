#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet import schema
from magicbullet.models import Item

class Language(Item):
    
    iso_code = schema.String(
        required = True,
        unique = True,
        max = 64
    )
        
    fallback_languages = schema.Collection(
        items = "magicbullet.models.Language"
    )

