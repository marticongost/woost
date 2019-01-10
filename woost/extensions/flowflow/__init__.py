#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from woost.models import Extension


class FlowFlowExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"Permet enriquir pàgines i enllaços amb atributs HTML "
            u"descriptius.",
            "ca"
        )
        self.set("description",
            u"Permite enriquecer páginas y enlaces con atributos HTML "
            u"descriptivos.",
            "es"
        )
        self.set("description",
            u"Adds descriptive HTML attributes to pages and links.",
            "en"
        )

    def _load(self):
        from woost.extensions.flowflow import (
            configuration,
            flowflowblock
        )

