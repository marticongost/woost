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
from cocktail.translations import (
    translations,
    set_language
)
from cocktail.language import (
    get_content_language,
    set_content_language
)
from cocktail.html import Element
from cocktail import schema
from woost.models import (
    get_current_user,
    ReadPermission,
    Site
)
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from woost.controllers.backoffice.contentcontroller \
    import ContentController
from woost.controllers.backoffice.deletecontroller import DeleteController
from woost.controllers.backoffice.ordercontroller import OrderController
from woost.controllers.backoffice.movecontroller import MoveController


class BackOfficeController(BaseBackOfficeController):

    _cp_config = BaseBackOfficeController.copy_config()
    _cp_config["rendering.engine"] = "cocktail"
    
    _edit_stacks_manager_class = \
        "woost.controllers.backoffice.editstack.EditStacksManager"

    default_section = "content"

    content = ContentController    
    delete = DeleteController
    order = OrderController
    move = MoveController
    
    def submit(self):
        raise cherrypy.HTTPRedirect(
            self.contextual_uri(self.default_section) + "?" + view_state())

    @event_handler
    def handle_traversed(cls, event):
        controller = event.source
        controller.context["edit_stacks_manager"] = \
            resolve(controller._edit_stacks_manager_class)()

    @event_handler
    def handle_before_request(cls, event):
        user = get_current_user()
        language = \
            user and user.prefered_language or Site.main.backoffice_language
        set_language(language)
        set_content_language(language)

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
                        "woost.backoffice invalid item preview", 
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
                original_publishable = self.context["publishable"],
                publishable = node.item
            )
            
            controller = node.item.resolve_controller()

            if controller is None:
                raise cherrypy.NotFound()

            if isinstance(controller, type):
                controller = controller()

            return controller()

    @cherrypy.expose
    def editor_attachments(self, **kwargs):
        
        cms = self.context["cms"]
        node = self.stack_node
        attachments = schema.get(node.form_data, "attachments", default = None)

        resource_type = self.params.read(schema.String("resource_type"))
        language = self.params.read(schema.String("language"))
        
        output = []
        cherrypy.response.headers["Content-Type"] = "text/javascript"

        if attachments:
            for attachment in attachments:
                if attachment.resource_type == resource_type:
                    output.append(
                        [
                            attachment.get("title", language),
                            cms.uri(attachment)
                        ]
                    )

        if resource_type == "image":
            return "var tinyMCEImageList = %s" % (dumps(output))
        else:
            return "var tinyMCELinkList = %s" % (dumps(output))

