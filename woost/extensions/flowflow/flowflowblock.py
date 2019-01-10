#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from woost.models import Block, Configuration


class FlowFlowBlock(Block):

    views = ["woost.extensions.flowflow.FlowFlow"]

    members_order = [
        "stream_id"
    ]

    stream_id = schema.Integer(
        required = True,
        min = 1
    )

    def init_view(self, view):
        Block.init_view(self, view)
        config = Configuration.instance
        view.flow_flow_url = config.flow_flow_url
        view.stream_id = self.stream_id

