#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail import schema
from sitebasis.models.document import Document


class StandardPage(Document):
    
    body = schema.String(
        translated = True,
        listed_by_default = False,        
        edit_control = "sitebasis.views.RichTextEditor"
    )