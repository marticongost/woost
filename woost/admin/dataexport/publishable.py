#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Publishable
from .dataexport import Export

@Export.fields_for(Publishable)
def publishable_fields(exporter, model, ref = False):
    yield (lambda obj, path: ("_url", obj.get_uri()))

