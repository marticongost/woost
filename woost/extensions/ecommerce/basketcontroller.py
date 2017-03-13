#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
import cherrypy
from cocktail.modeling import extend, call_base
from cocktail.translations import translations
from cocktail import schema
from cocktail.controllers import (
    Controller,
    request_property,
    FormProcessor,
    Form,
    reload_request_url
)
from woost.controllers.notifications import Notification
from woost.extensions.ecommerce.ecommercepurchase import ECommercePurchase
from woost.extensions.ecommerce.basket import Basket
from woost.extensions.ecommerce.orderstepcontroller import (
    ProceedForm
)

translations.load_bundle("woost.extensions.ecommerce.basketcontroller")


class BasketController(FormProcessor, Controller):

    @request_property
    def action(self):

        delete_purchase = cherrypy.request.params.get("delete_purchase", None)

        if delete_purchase:
            cherrypy.request.params["purchase"] = delete_purchase
            return "delete_purchase"

        return FormProcessor.action(self)

    class SetQuantitiesForm(Form):
        """Update the number of units for each purchase."""

        actions = "set_quantities", "proceed"

        @request_property
        def model(self):
            model = schema.Schema("SetQuantitiesForm", members = [
                schema.Collection("quantity",
                    items = schema.Integer(min = 1, required = True),
                    length = len(Basket.get().purchases)
                )
            ])

            @extend(model["quantity"].items)
            def translate_error(member, error, language = None, **kwargs):
                if isinstance(error, schema.exceptions.MinValueError):
                    return translations(
                        "woost.extensions.ecommerce.basketcontroller."
                        "min_quantity_error"
                        language,
                        **kwargs
                    )
                else:
                    return call_base(error, language, **kwargs)

            return model

        def submit(self):
            Form.submit(self)

            for purchase, quantity in zip(
                Basket.get().purchases,
                self.instance["quantity"]
            ):
                purchase.quantity = quantity

            Basket.store()

        def after_submit(self):
            Notification(
                translations(
                    "woost.extensions.ecommerce.basketcontroller."
                    "set_quantities"
                ),
                category = "success"
            ).emit()

            if self.controller.action != "proceed":
                reload_request_url()

    class NextStepForm(ProceedForm):
        process_after = "set_quantities_form",

    class DeletePurchaseForm(Form):
        """A form that removes a product from the shopping basket."""

        actions = "delete_purchase",
        deleted_product = None

        @request_property
        def model(self):
            return schema.Schema("DeletePurchaseForm", members = [
                schema.Reference("purchase",
                    type = ECommercePurchase,
                    required = True,
                    enumeration = lambda ctx: Basket.get().purchases
                )
            ])

        def submit(self):
            Form.submit(self)
            purchase = self.instance["purchase"]
            self.deleted_product = purchase.product
            purchase.delete()
            Basket.store()

        def after_submit(self):
            purchase = self.instance["purchase"]
            Notification(
                translations(
                    "woost.extensions.ecommerce.basketcontroller."
                    "delete_purchase",
                    product = self.deleted_product
                ),
                category = "success"
            ).emit()
            reload_request_url()

    class EmptyBasketForm(Form):
        """A form that removes all products from the shopping basket."""

        actions = "empty_basket",

        def submit(self):
            Basket.empty()

        def after_submit(self):
            Notification(
                translations(
                    "woost.extensions.ecommerce.basketcontroller."
                    "empty_basket"
                ),
                category = "success"
            ).emit()
            reload_request_url()

