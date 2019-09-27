"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.controllers import Controller, json_out, read_json

from woost import app
from woost.admin.dataimport import Import
from woost.admin.dataexport import Export


class PasteController(Controller):

    @json_out
    def __call__(self, **kwargs):

        if cherrypy.request.method != "POST":
            raise cherrypy.HTTPError(405, "Expected a POST request")

        user = app.user
        data = read_json()
        exp = Export(include_slots=True)
        objects = []

        for obj_data in data["objects"]:
            obj_data.pop("id", None)
            obj_data.pop("global_id", None)
            obj = Import(obj_data, user=user).obj
            obj.require_id()
            objects.append(exp.export_object(obj))

        return {"objects": objects}

