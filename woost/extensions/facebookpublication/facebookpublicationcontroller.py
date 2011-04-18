#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import sys
import cherrypy
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail import schema
from cocktail.persistence import datastore
from cocktail.controllers import (
    request_property,
    get_parameter,
    Location
)
from woost.models import Publishable, get_current_user
from woost.controllers.notifications import notify_user
from woost.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController
from woost.extensions.facebookpublication import FacebookPublicationExtension
from woost.extensions.facebookpublication.facebookpublicationtarget \
    import FacebookPublicationTarget
from woost.extensions.facebookpublication.facebookpublicationpermission \
    import FacebookPublicationPermission


class FacebookPublicationController(BaseBackOfficeController):

    notice_summary_threshold = 4
    view_class = "woost.extensions.facebookpublication.FacebookPublicationView"

    @request_property
    def form_schema(self):
        return schema.Schema("FacebookPublicationForm", members = [
            schema.Collection("publication_targets",
                items = schema.Reference(
                    type = FacebookPublicationTarget,
                    required = True,
                    enumeration = lambda ctx: self.allowed_publication_targets
                ),
                min = 1,
                default = schema.DynamicDefault(
                    lambda: self.allowed_publication_targets
                )
            )
        ])

    @request_property
    def form_data(self):
        return get_parameter(
            self.form_schema,
            errors = "ignore",
            undefined = "set_none" if self.submitted else "set_default"
        )

    @request_property
    def form_errors(self):
        return schema.ErrorList(
            []
            if not self.submitted
            else self.form_schema.get_errors(self.form_data)
        )

    @event_handler
    def handle_before_request(cls, e):
        
        controller = e.source
        
        if not controller.allowed_publication_targets:
            raise cherrypy.HTTPError(403, "Forbidden")

    @request_property
    def allowed_publication_targets(self):
            
        from woost.extensions.facebookpublication \
            import FacebookPublicationExtension

        user = get_current_user()

        return [fb_target
                for fb_target in FacebookPublicationExtension.instance.targets
                if fb_target.auth_token
                and all(
                    user.has_permission(
                        FacebookPublicationPermission,
                        target = publishable,
                        publication_target = fb_target
                    )
                    for publishable in self.selection
                )]

    @request_property
    def selection(self):
        return get_parameter(
            schema.Collection("selection", 
                items = schema.Reference(
                    type = Publishable,
                    required = True
                ),
                min = 1
            ),
            errors = "raise"
        )

    @request_property
    def submitted(self):
        return cherrypy.request.method == "POST"

    @request_property
    def valid(self):
        return self.action != "publish" \
            or self.form_schema.validate(self.form_data)

    @request_property
    def action(self):
        return cherrypy.request.params.get("action")

    def submit(self):
        
        if self.action == "close":
            self.go_back()

        targets = self.form_data["publication_targets"]
        published_everything = True

        for target in targets:
            successful = []
            failed = []

            for publishable in self.selection:
                try:
                    target.publish(publishable)
                except Exception, ex:
                    sys.stderr.write(str(ex) + "\n")
                    failed.append(publishable)
                    published_everything = False
                else:
                    successful.append(publishable)

            for items, outcome in (
                (successful, "success"),
                (failed, "error")
            ):
                if not items:
                    continue

                notify_user(
                    translations(
                        "woost.extensions.facebookpublication."
                        "publication_%s_notice" % outcome,
                        target = target,
                        items = items,
                        summarize = (len(items) >= self.notice_summary_threshold)
                    ),
                    category = outcome,
                    transient = False
                )

        if published_everything:
            if self.edit_stack:
                self.edit_stack.go()
            else:
                self.go_back()

    @request_property
    def output(self):
        output = BaseBackOfficeController.output(self)
        output.update(
            selection = self.selection,
            form_schema = self.form_schema,
            form_data = self.form_data,
            form_errors = self.form_errors
        )
        return output

