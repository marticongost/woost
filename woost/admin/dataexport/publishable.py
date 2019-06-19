#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import PublishableObject
from .dataexport import Export

@Export.fields_for(PublishableObject)
def publishable_fields(exporter, model, ref = False):
    yield (lambda obj, path: ("_url", obj.get_uri()))

