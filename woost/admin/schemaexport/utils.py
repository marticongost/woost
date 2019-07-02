#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.javascriptserializer import dumps


def iter_last(items):
    iterator = iter(items)
    try:
        prev = next(iterator)
    except StopIteration:
        pass
    else:
        for item in iterator:
            yield prev, False
            prev = item
        yield prev, True


def export_view_names(target):
    from woost.admin.views import available_views
    return (
        "[woost.admin.views.views]",
        dumps([
            view.name
            for view in available_views(target)
        ])
    )

