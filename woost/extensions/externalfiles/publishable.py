#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from woost.models import Publishable, File, Configuration

_get_uri = Publishable.get_uri

def get_uri(self, **kwargs):

    if isinstance(self, File) and kwargs.get("host") in (None, "!", "?"):
        kwargs["host"] = \
            Configuration.instance.get_setting("external_files_host")

    return _get_uri(self, **kwargs)

Publishable.get_uri = get_uri

