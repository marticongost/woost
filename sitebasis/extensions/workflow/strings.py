#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from cocktail.translations import translations

translations.define("Action transition",
    ca = u"Establir estat",
    es = u"Establecer estado",
    en = u"Set state"
)

translations.define(
    "sitebasis.controllers.backoffice.useractions.TransitionAction state set",
    ca = lambda item: u"S'ha canviat l'estat de <em>%s</em> a <em>%s</em>"
        % (translations(item, "ca"), translations(item.state, "ca")),
    es = lambda item: u"Se ha cambiado el estado de <em>%s</em> a <em>%s</em>"
        % (translations(item, "es"), translations(item.state, "es")),
    en = lambda item: u"State of <em>%s</em> changed to <em>%s</em>"
        % (translations(item, "en"), translations(item.state, "en"))
)

# Item
#------------------------------------------------------------------------------
translations.define("Item.state",
    ca = u"Estat",
    es = u"Estado",
    en = u"State"
)

# AccessRule
#------------------------------------------------------------------------------
translations.define("AccessRule.target_state",
    ca = u"Estat de l'element",
    es = u"Estado del elemento",
    en = u"Target's state"
)

translations.define("AccessRule.target_new_state",
    ca = u"Estat destí de l'element",
    es = u"Estado destino del elemento",
    en = u"Target's destination state"
)

# Trigger
#------------------------------------------------------------------------------
translations.define("Trigger.item_states",
    ca = u"Estats",
    es = u"Estados",
    en = u"States"
)

translations.define("Trigger.item_previous_states",
    ca = u"Estats d'origen",
    es = u"Estados de origen",
    en = u"Source states"
)

# State
#------------------------------------------------------------------------------
translations.define("State",
    ca = u"Estat",
    es = u"Estado",
    en = u"State"
)

translations.define("State-plural",
    ca = u"Estats",
    es = u"Estados",
    en = u"States"
)

translations.define("State.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("State.outgoing",
    ca = u"Estats destí",
    es = u"Estados destino",
    en = u"Target states"
)

translations.define("State.incomming",
    ca = u"Estats origen",
    es = u"Estados origen",
    en = u"Source states"
)

# SetStateTriggerResponse
#------------------------------------------------------------------------------
translations.define("SetStateTriggerResponse",
    ca = u"Resposta amb canvi d'estat",
    es = u"Respuesta con cambio de estado",
    en = u"Response with state change"
)

translations.define("SetStateTriggerResponse-plural",
    ca = u"Respostes amb canvi d'estat",
    es = u"Respuestas con cambio de estado",
    en = u"Responses with state change"
)

translations.define("SetStateTriggerResponse.target_state",
    ca = u"Estat de destí",
    es = u"Estado de destino",
    en = u"Destination state"
)

