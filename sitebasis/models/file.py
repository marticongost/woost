#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail import schema
from sitebasis.models.document import Document

class File(Document):
 
    default_handler = "sitebasis.controllers.filehandler.FileHandler"

    members_order = "file_path", "file_language", "mime_type", "documents"

    file_path = schema.String(required = True)

    file_language = schema.Reference(
        type = "sitebasis.models.Language"
    )
    
    mime_type = schema.String(
        required = True
    )

    documents = schema.Collection(
        items = "sitebasis.models.Document",
        bidirectional = True
    )
  

