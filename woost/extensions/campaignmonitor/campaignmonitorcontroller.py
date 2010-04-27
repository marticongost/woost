#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			March 2010
"""
import cherrypy
from cocktail import schema
from cocktail.modeling import cached_getter
from cocktail.pkgutils import import_object
from cocktail.controllers import FormControllerMixin, context
from woost.controllers.documentcontroller import DocumentController
from woost.extensions.campaignmonitor import CampaignMonitorExtension
from woost.extensions.campaignmonitor.campaign_monitor_api import \
    CampaignMonitorApi


class CampaignMonitorController(FormControllerMixin, DocumentController):

    campaign_monitor_errors = None

    @cached_getter
    def form_model(self):
        return import_object(self.context["publishable"].subscription_form)

    @cached_getter
    def form_schema(self):
        form_schema = FormControllerMixin.form_schema(self)
        publishable = self.context["publishable"]

        form_schema.add_member(schema.Reference(
            "list",
            type = "woost.extensions.campaignmonitor.campaignmonitorlist."
                "CampaignMonitorList",
            required = True,
            enumeration = publishable.lists,
            default = publishable.lists[0]
        ))
        form_schema.members_order = "name", "email", "list"

        return form_schema

    @cached_getter
    def custom_fields(self):
        return {}

    def submit(self):
        FormControllerMixin.submit(self)

        extension = CampaignMonitorExtension.instance
        cmlist = self.form_data["list"]
        email = self.form_data["email"].encode("utf-8")
        name = self.form_data["name"].encode("utf-8")
 
        api = CampaignMonitorApi(
            extension.api_key,
            extension.client_id
        )

        try:
            user_subscribed = api.subscribers_get_is_subscribed(
                cmlist.list_id,
                email
            )
        except CampaignMonitorApi.CampaignMonitorApiException:
            user_subscribed = False

        # Obtain custom fields
        new_custom_fields = self.custom_fields

        if user_subscribed:
            response = api.subscribers_get_single_subscriber(
                cmlist.list_id,
                email
            )
            subscriber = response.get("Subscribers.GetSingleSubscriber")
            custom_fields = subscriber[0].get("CustomFields")
        else:
            custom_fields = {}

        custom_fields.update(**new_custom_fields)

        # Encode custom fields
        encoded_custom_fields = {}
        for key, value in custom_fields.items():
            encoded_key = (
                key.encode("utf-8") if isinstance(key, unicode) else key
            )
            encoded_value = (
                value.encode("utf-8") if isinstance(value, unicode) else value
            )
            custom_fields[encoded_key] = encoded_value

        try:
            api.subscriber_add_and_resubscribe(
                cmlist.list_id,
                email,
                name,
                encoded_custom_fields
            )
        except CampaignMonitorApi.CampaignMonitorApiException:
            # TODO: Capture the error code and show the correct message
            self.campaign_monitor_errors = True
        else:

            if user_subscribed and cmlist.confirmation_success_page:
                uri = context["cms"].uri(cmlist.confirmation_success_page)
            elif not user_subscribed and cmlist.pending_page:
                uri = context["cms"].uri(cmlist.pending_page)
            else:
                uri = context["cms"].uri(context["publishable"])

            raise cherrypy.HTTPRedirect(uri.encode("utf-8"))

    @cached_getter
    def output(self):

        output = DocumentController.output(self)
        output.update(
            campaign_monitor_errors = self.campaign_monitor_errors
        )

        return output

