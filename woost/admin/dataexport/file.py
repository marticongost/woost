#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import File, Publishable
from .dataexport import Export, object_field


@Export.fields_for(File)
def file_fields(exporter, model, ref = False):
    yield (lambda obj, path:
        ("_size_label", model.file_size.translate_value(obj.file_size))
    )
    yield (lambda obj, path:
        ("_upload", obj._v_upload_id) if obj._v_upload_id else None
    )
    if ref:
        yield object_field(exporter, File.file_name)
        yield object_field(exporter, Publishable.resource_type)

