#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
import cherrypy
from simplejson import dumps
from cocktail.pkgutils import resolve
from cocktail.events import event_handler
from cocktail.controllers import view_state
from cocktail import schema
from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from sitebasis.controllers.backoffice.contentcontroller \
    import ContentController
from sitebasis.controllers.backoffice.deletecontroller import DeleteController
from sitebasis.controllers.backoffice.ordercontroller import OrderController
from sitebasis.controllers.backoffice.movecontroller import MoveController


class BackOfficeController(BaseBackOfficeController):

    _cp_config = BaseBackOfficeController.copy_config()
    _cp_config["rendering.engine"] = "cocktail"
    
    _edit_stacks_manager_class = \
        "sitebasis.controllers.backoffice.editstack.EditStacksManager"

    default_section = "content"

    content = ContentController    
    delete = DeleteController
    order = OrderController
    move = MoveController
    
    def submit(self):
        raise cherrypy.HTTPRedirect(
            self.document_uri(self.default_section) + "?" + view_state())

    @event_handler
    def handle_traversed(cls, event):
        controller = event.source
        controller.context["edit_stacks_manager"] = \
            resolve(controller._edit_stacks_manager_class)()

    @event_handler
    def handle_after_request(cls, event):
        
        if event.error is None:
            controller = event.source
            edit_stacks_manager = controller.context["edit_stacks_manager"]
            edit_stack = edit_stacks_manager.current_edit_stack
            
            if edit_stack is not None:
                edit_stacks_manager.preserve_edit_stack(edit_stack)

    @cherrypy.expose
    def render_preview(self, **kwargs):
        node = self.stack_node
        self.restrict_access(
            action = "read",
            target_instance = node.item
        )
        
        node.import_form_data(node.form_data, node.item)
        
        self.context.update(
            original_document = self.context["document"],
            document = node.item
        )
        
        document_controller = node.item.handler()
        return document_controller()

    @cherrypy.expose
    def document_images(self, **kwargs):
        cherrypy.response.headers["Content-Type"] = "text/javascript"
        node = self.stack_node
        resources = schema.get(node.form_data, "attachments")
        output = []
        for resource in resources:
            if resource.resource_type == "image":
                output.append([resource.title, resource.uri])

        return "var tinyMCEImageList = %s" % (dumps(output))

    @cherrypy.expose
    def document_files(self, **kwargs):
        cherrypy.response.headers["Content-Type"] = "text/javascript"
        node = self.stack_node
        resources = schema.get(node.form_data, "attachments")
        output = []
        for resource in resources:
            if resource.resource_type == "document":
                output.append([resource.title, resource.uri])

        return "var tinyMCELinkList = %s" % (dumps(output))

