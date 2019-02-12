#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.controllers import (
    request_property,
    redirect,
    Form
)
from woost import app


class OrderStepForm(Form):

    @request_property
    def order_steps(self):
        return app.website.ecommerce_order_steps

    @request_property
    def current_step(self):
        return app.publishable

    @request_property
    def next_step(self):
        steps = self.order_steps
        pos = steps.index(self.current_step)
        if pos + 1 < len(steps):
            return steps[pos + 1]

    def proceed(self):
        next_step = self.next_step
        if next_step is not None:
            redirect(next_step.get_uri())


class ProceedForm(OrderStepForm):

    actions = "proceed",

    def after_submit(self):
        self.proceed()

