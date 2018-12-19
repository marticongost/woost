#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Change
from .dataexport import Export


class ItemStateExport(Export):

    def should_include_member(self, member):
        return Export.should_include_member(self, member) and member.versioned

    def export_object(self, obj, path = (), ref = False):
        data = Export.export_object(self, obj, path = path, ref = ref)
        data.pop("_class")
        data.pop("_thumbnail")
        return data


def _export_item_state(exporter, obj, path):

    target = obj.target
    state = obj.item_state

    if target is None or state is None:
        return None

    if not state:
        return {}

    return ItemStateExport(children_export = exporter).export_object(
        target.__class__(**state),
        path = path + (Change.item_state,)
    )

def _item_state_fields(exporter, member, ref):
    yield (
        lambda obj, path:
            (
                "item_state",
                _export_item_state(exporter, obj, path)
            )
    )

Export.member_fields[Change.item_state] = _item_state_fields

