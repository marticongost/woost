"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Style
from .dataexport import Export, object_field


@Export.fields_for(Style)
def file_fields(exporter, model, ref = False):
    if not ref:
        yield (lambda obj, path:
            ("class_name", obj.class_name)
        )

