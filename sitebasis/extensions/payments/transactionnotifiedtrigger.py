#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from cocktail.events import when
from cocktail import schema
from sitebasis.models.trigger import (
    Trigger,
    trigger_responses
)
from sitebasis.extensions.payments.paymentgateway import PaymentGateway


class TransactionNotifiedTrigger(Trigger):
    instantiable = True


@when(PaymentGateway.transaction_notified)
def launch_transaction_notification_triggers(event):
    trigger_responses(
        TransactionNotifiedTrigger,
        payment = event.payment
    )

