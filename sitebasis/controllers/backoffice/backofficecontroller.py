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
from cocktail.translations import translations
from cocktail.language import get_content_language
from cocktail.html import Element
from cocktail import schema
from sitebasis.models import get_current_user, ReadPermission
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
        
        get_current_user().require_permission(
            ReadPermission,
            target = node.item
        )
        
        node.import_form_data(
            node.form_data,
            node.item
        )
        
        errors = list(node.item.__class__.get_errors(node.item))

        if errors:
            message = Element("div",
                class_name = "preview-error-box",
                children = [
                    translations(
                        "sitebasis.backoffice invalid item preview", 
                        get_content_language()
                    ),
                    Element("ul", children = [
                        Element("li", children = [translations(error)])
                        for error in errors
                    ])
                ]
            )
            message.add_resource("/resources/styles/backoffice.css")           
            return message.render_page()        
        else:

            self.context.update(
                original_document = self.context["document"],
                document = node.item
            )
            
            document_controller = node.item.handler()
            return document_controller()

    @cherrypy.expose
    def document_resources(self, **kwargs):
        cherrypy.response.headers["Content-Type"] = "text/javascript"
        node = self.stack_node
        resources = schema.get(node.form_data, "attachments", default = None)
        output = []        
        if resources:
            for resource in resources:
                if resource.resource_type == kwargs["resource_type"]:
                    output.append([resource.title, resource.uri])

        if kwargs["resource_type"] == "image":
            return "var tinyMCEImageList = %s" % (dumps(output))
        else:
            return "var tinyMCELinkList = %s" % (dumps(output))
        

