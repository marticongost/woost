#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.admin.models import Admin
from .dataexport import Export


class AdminExport(Export):
    pass


@AdminExport.fields_for(Admin)
def admin_fields(exporter, model, ref = False):
    from woost.admin import views, partitioning
    if not ref:
        yield (lambda obj, path:
            ("_root_section", obj.get_root_section().export_data())
        )
        yield (lambda obj, path:
            ("_views", [
                view.export_data()
                for view in views.available_views()
            ])
        )
        yield (lambda obj, path:
            ("_partitioning_methods", [
                method.export_data()
                for method in partitioning.available_methods()
            ])
        )

