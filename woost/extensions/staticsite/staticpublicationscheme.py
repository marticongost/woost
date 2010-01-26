#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
from mimetypes import guess_extension
from cocktail import schema
from woost.models import (
    Publishable,
    PublicationScheme,
    PathResolution
)


class StaticPublicationScheme(PublicationScheme):
    """A publication scheme that mimics a static filesystem layout."""

    instantiable = True

    def resolve_path(self, path):
        
        if len(path) == 1:
            return None

        step = path[0]
        pos = step.rfind(".")
            
        if pos == -1:
            return None

        id = step[:pos]
        try:
            id = int(id)
        except:
            return None
        
        publishable = Publishable.get_instance(id)

        if publishable and publishable.mime_type:
            ext = step[pos:]
            if guess_extension(publishable.mime_type, False) == ext:
                return PathResolution(self, publishable, [step])

    def get_path(self, publishable, language = None):
        if publishable.mime_type:
            extension = guess_extension(publishable.mime_type, False)
            if extension:
                return str(publishable.id) + extension

