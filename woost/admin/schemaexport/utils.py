#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.javascriptserializer import dumps
from woost.admin.views import available_views

def iter_last(items):
    iterator = iter(items)
    try:
        prev = iterator.next()
    except StopIteration:
        pass
    else:
        for item in iterator:
            yield prev, False
            prev = item
        yield prev, True

def export_view_names(target):
    return (
        u"[woost.admin.views.views]",
        dumps([
            view.name
            for view in available_views(target)
        ])
    )

