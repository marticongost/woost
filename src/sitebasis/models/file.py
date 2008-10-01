#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet import schema
from magicbullet.models.document import Document

class File(Document):
 
    members_order = "file_path", "translation_file_path"

    file_path = schema.String()

    translation_file_path = schema.String(translated = True)

    documents = schema.Collection(
        items = "magicbullet.models.Document",
        bidirectional = True
    )

