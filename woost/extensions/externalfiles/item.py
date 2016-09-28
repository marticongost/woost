#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from woost.models import Item, Configuration

_get_image_uri = Item.get_image_uri

def get_image_uri(self, *args, **kwargs):

    host = kwargs.get("host")

    if host in (None, "!", "?"):
        kwargs["host"] = \
            Configuration.instance.get_setting("external_files_host")

    return _get_image_uri(self, *args, **kwargs)

Item.get_image_uri = get_image_uri

