#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.admin.models import Admin
from .dataexport import Export


class AdminExport(Export):
    pass


@AdminExport.fields_for(Admin)
def admin_fields(exporter, model, ref = False):
    from woost.admin.views import available_views
    if not ref:
        yield (lambda obj, path:
            ("_root_section", obj.get_root_section().export_data())
        )
        yield (lambda obj, path:
            ("_views", [
                view.export_data()
                for view in available_views()
            ])
        )

