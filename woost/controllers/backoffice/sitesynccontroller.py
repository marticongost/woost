#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import cherrypy
from cocktail.events import event_handler
from cocktail import schema
from cocktail.controllers import (
    FormProcessor,
    Form,
    request_property
)
from cocktail.persistence import transactional
from woost.models import (
    Synchronization,
    Item,
    User,
    get_current_user,
    InstallationSyncPermission
)
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController


class SiteSyncController(FormProcessor, BaseBackOfficeController):

    @request_property
    def synchronization(self):
        return Synchronization()

    @event_handler
    def handle_traversed(cls, e):
        get_current_user().require_permission(InstallationSyncPermission)

    @cherrypy.expose
    @transactional()
    def manifest(self):
        cherrypy.response.headers["Content-Type"] = "text/plain"
        for global_id, object_hash in self.synchronization.process_manifest():
            yield "%s %s\n" % (global_id, object_hash)

    @cherrypy.expose
    def state(self, identifiers):
        cherrypy.response.headers["Content-Type"] = "application/json"

        glue = ""
        yield "{"
        
        for global_id in identifiers.split(","):
            obj = Item.require_instance(global_id = global_id)
            yield '%s"%s":' % (glue, global_id)
            yield self.synchronization.serialize_object_state(obj)
            glue = ","

        yield "}"

    class SyncForm(Form):

        model = schema.Schema("SiteSync", members = [
            schema.URL("site_url",
                required = True
            ),
            schema.String("remote_user",
                required = True
            ),
            schema.String("remote_password",
                required = True,
                edit_control = "cocktail.html.PasswordBox"
            )
        ])

        def submit(self):
            Form.submit(self)
            pass

