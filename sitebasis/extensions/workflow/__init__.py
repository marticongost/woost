#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail.persistence import datastore
from sitebasis.models import Extension

translations.define("WorkflowExtension",
    ca = u"Circuïts de treball",
    es = u"Circuitos de trabajo",
    en = u"Workflow"
)

translations.define("WorkflowExtension-plural",
    ca = u"Circuïts de treball",
    es = u"Circuitos de trabajo",
    en = u"Workflow"
)


class WorkflowExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet construïr circuïts de treball, mitjançant la definició
            d'estats i transicions pels elements.""",
            "ca"
        )
        self.set("description",
            u"""Permite construir circuitos de trabajo, mediante la definición
            de estados y transiciones para los elementos.""",
            "es",
        )
        self.set("description",
            u"""Allows the set up of workflows, based on a system of item
            states and transitions..""",
            "en"
        )

    @event_handler
    def handle_loading(cls, event):
        
        from sitebasis.extensions.workflow import (
            strings,
            state,
            transition,
            transitionpermission,
            transitiontrigger,
            setstatetriggerresponse,
            useractions
        )

