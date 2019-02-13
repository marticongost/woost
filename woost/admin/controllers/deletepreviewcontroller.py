#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import json
import cherrypy
from cocktail.persistence import delete_dry_run
from cocktail.controllers import Controller, request_property
from woost import app
from woost.models import DeletePermission
from woost.admin.dataexport import Export
from woost.admin.controllers.utils import resolve_object_ref


class DeletePreviewController(Controller):

    def __call__(self, id_list):

        cherrypy.response.headers["Content-Type"] = \
            "application/json; charset=utf-8"

        if not id_list:
            raise cherrypy.HTTPError(400, "No objects specified")

        root = []
        data = {"root": root}

        if isinstance(id_list, str):
            id_list = [id_list]

        for id in id_list:
            obj = resolve_object_ref(id)
            if app.user.has_permission(DeletePermission, target = obj):
                dry_run = delete_dry_run(obj)
                if dry_run:
                    root.append(self.export_node(dry_run))

        data["blocked"] = self.blocked
        return json.dumps(data)

    def export_node(self, node):

        if node["blocking"]:
            self.blocked = True

        x = Export()
        data = x.export_object(node["item"], ref = True)
        data["_block_delete"] = dict(
            (
                member.name,
                x.export_object_list(values, ref = True)
            )
            for member, values in node["blocking"].items()
        )
        data["_cascade_delete"] = dict(
            (
                member.name,
                [
                    self.export_node(subnode)
                    for subnode in subnodes
                ]
            )
            for member, subnodes in node["cascade"].items()
        )
        return data

    @request_property
    def blocked(self):
        return False

