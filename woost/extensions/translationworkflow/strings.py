#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.stringutils import decapitalize
from cocktail.translations import translations
from cocktail.translations.helpers import plural2, ca_possessive, join
from woost.translations.strings \
    import content_permission_translation_factory

translations.define("woost.type_groups.translation_workflow",
    ca = u"Circuït de traducció",
    es = u"Circuito de traducción",
    en = u"Translation workflow"
)

translations.define("woost.actions.translation_workflow_transition",
    ca = u"Canviar estat",
    es = u"Cambiar estado",
    en = u"Change state"
)

translations.define("woost.actions.translation_workflow_requests",
    ca = u"Peticions de traducció",
    es = u"Peticiones de traducción",
    en = u"Translation requests"
)

# Configuration
#------------------------------------------------------------------------------
translations.define("Configuration.translation_workflow_paths",
    ca = u"Camins de traducció",
    es = u"Caminos de traducción",
    en = u"Translation paths"
)

translations.define("Configuration.translation_workflow_paths-explanation",
    ca = u"Emparellaments d'idiomes per generar peticions de traducció.",
    es = u"Emparejamientos de idiomas para generar peticiones de traducción.",
    en = u"Language pairings to generate translation requests."
)

# Item
#------------------------------------------------------------------------------
translations.define("Item.translation_requests",
    ca = u"Peticions de traducció",
    es = u"Peticiones de traducción",
    en = u"Translation requests"
)

# Role
#------------------------------------------------------------------------------
translations.define("Role.translation_workflow_relevant_states",
    ca = u"Estats rellevants del circuït de traducció",
    es = u"Estados relevantes del circuito de traducción",
    en = u"Translation workflow relevant states"
)

translations.define("Role.translation_workflow_default_state",
    ca = u"Estat per defecte del circuït de traducció",
    es = u"Estado por defecto del circuito de traducción",
    en = u"Translation workflow default state"
)

# TranslationWorkflowRequest
#------------------------------------------------------------------------------
translations.define("TranslationWorkflowRequest",
    ca = u"Petició de traducció",
    es = u"Petición de traducción",
    en = u"Translation request"
)

translations.define("TranslationWorkflowRequest-plural",
    ca = u"Peticions de traducció",
    es = u"Peticiones de traducción",
    en = u"Translation requests"
)

translations.define("TranslationWorkflowRequest.tabs.all",
    ca = u"Totes",
    es = u"Todas",
    en = u"All"
)

translations.define("TranslationWorkflowRequest.translated_item",
    ca = u"Element a traduir",
    es = u"Elemento a traducir",
    en = u"Translated item"
)

translations.define("TranslationWorkflowRequest.source_language",
    ca = u"Idioma origen",
    es = u"Idioma origen",
    en = u"Idioma destino"
)

translations.define("TranslationWorkflowRequest.target_language",
    ca = u"Idioma destí",
    es = u"Idioma destino",
    en = u"Target language"
)

translations.define("TranslationWorkflowRequest.state",
    ca = u"Estat",
    es = u"Estado",
    en = u"State"
)

translations.define("TranslationWorkflowRequest.assigned_translator",
    ca = u"Traductor assignat",
    es = u"Traductor asignado",
    en = u"Assigned translator"
)

translations.define("TranslationWorkflowRequest.translated_values",
    ca = u"Traducció",
    es = u"Traducción",
    en = u"Translation"
)

translations.define("TranslationWorkflowRequest.comments",
    ca = u"Comentaris",
    es = u"Comentarios",
    en = u"Comments"
)

translations.define(
    "woost.extensions.translationworkflow.request."
    "TranslationWorkflowRequest-instance",
    ca = lambda instance, referer = None, **kwargs:
        (
            (
                u"Traducció "
                + ca_possessive(
                     '"%s" '
                     % translations(instance.translated_item)
                )
            )
            if referer is None
            else ""
        )
        + (
            instance.source_language
            and ca_possessive(
                decapitalize(
                    translations("locale", locale = instance.source_language)
                )
            )
            or u"?"
        )
        + u" a "
        + (
            instance.target_language
            and decapitalize(
                translations("locale", locale = instance.target_language)
            )
            or u"?"
        ),
    es = lambda instance, referer = None, **kwargs:
        (
            u'Traducción de "%s" de '
            % translations(instance.translated_item)
            if referer is None
            else u"De "
        )
        + (
            instance.source_language
            and decapitalize(
                translations("locale", locale = instance.source_language)
            )
            or u"?"
        )
        + u" a "
        + (
            decapitalize(
                translations("locale", locale = instance.target_language)
            )
            if instance.target_language
            else "?"
        ),
    en = lambda instance, referer = None, **kwargs:
        (
            u'Translation of "%s" from '
            % translations(instance.translated_item)
            if referer is None
            else u"From "
        )
        + (
            instance.source_language
            and translations("locale", locale = instance.source_language)
            or u"?"
        )
        + u" to "
        + (
            instance.target_language
            and translations("locale", locale = instance.target_language)
            or u"?"
        )
)

# TranslationWorkflowState
#------------------------------------------------------------------------------
translations.define("TranslationWorkflowState",
    ca = u"Estat del circuït de traducció",
    es = u"Estado del circuito de traducción",
    en = u"Translation workflow state"
)

translations.define("TranslationWorkflowState-plural",
    ca = u"Estats del circuït de traducció",
    es = u"Estados del circuito de traducción",
    en = u"Translation workflow states"
)

translations.define("TranslationWorkflowState.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("TranslationWorkflowState.plural_title",
    ca = u"Nom en plural",
    es = u"Nombre en plural",
    en = u"Plural name"
)

translations.define("TranslationWorkflowState.incomming_transitions",
    ca = u"Transicions entrants",
    es = u"Transiciones entrantes",
    en = u"Incomming transitions"
)

translations.define("TranslationWorkflowState.outgoing_transitions",
    ca = u"Transicions de sortida",
    es = u"Transiciones de salida",
    en = u"Outgoing transitions"
)

translations.define("TranslationWorkflowState.state_after_source_change",
    ca = u"Nou estat quan es modifiqui el text original",
    es = u"Nuevo estado cuando se modifique el texto original",
    en = u"State after the translated item is modified"
)

# TranslationWorkflowTransition
#------------------------------------------------------------------------------
translations.define("TranslationWorkflowTransition",
    ca = u"Transició del circuït de traducció",
    es = u"Transición del circuito de traducción",
    en = u"Translation workflow transition"
)

translations.define("TranslationWorkflowTransition-plural",
    ca = u"Transicions del circuït de traducció",
    es = u"Transiciones del circuito de traducción",
    en = u"Translation workflow transitions"
)

translations.define("TranslationWorkflowTransition.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("TranslationWorkflowTransition.source_states",
    ca = u"Estat origen",
    es = u"Estado origen",
    en = u"Source state"
)

translations.define("TranslationWorkflowTransition.source_states-explanation",
    ca = u"Els estats on comença la transició. Deixar en blanc per definir "
         u"una transició aplicable a tots els estats.",
    es = u"Los estados desde los que parte la transición. Dejar en blanco "
         u"para definir una transición aplicable a todos los estados.",
    en = u"The starting states for the transition. Leave blank to define a "
         u"transition that can be applied to any state."
)

translations.define("TranslationWorkflowTransition.target_state",
    ca = u"Estat destí",
    es = u"Estado destino",
    en = u"Target state"
)

translations.define("TranslationWorkflowTransition.icon",
    ca = u"Icona",
    es = u"Icono",
    en = u"Icon"
)

translations.define("TranslationWorkflowTransition.relative_order",
    ca = u"Ordre relatiu",
    es = u"Orden relativo",
    en = u"Relative order"
)

translations.define("TranslationWorkflowTransition.transition_schema",
    ca = u"Esquema de transició",
    es = u"Esquema de transición",
    en = u"Transition schema"
)

translations.define("TranslationWorkflowTransition.transition_code",
    ca = u"Codi de transició",
    es = u"Código de transición",
    en = u"Transition code"
)

translations.define(
    "woost.extensions.translationworkflow.transition_executed_notice",
    ca = lambda transition, requests:
        plural2(
            len(requests),
            u"Una petició passada",
            u"%d peticions passades" % len(requests)
        )
        + u" a l'estat <em>%s</em>."
          % decapitalize(translations(transition.target_state)),
    es = lambda transition, requests:
        plural2(
            len(requests),
            u"Una petición pasada",
            u"%d peticiones pasadas" % len(requests)
        )
        + u" al estado <em>%s</em>."
          % decapitalize(translations(transition.target_state)),
    en = lambda transition, requests:
        plural2(
            len(requests),
            u"One request",
            u"%d requests" % len(requests)
        )
        + u" transitioned to the <em>%s</em> state."
          % decapitalize(translations(transition.target_state))
)

# Transition controller
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.translationworkflow.transitionnode."
    "TranslationWorkflowTransitionNode-instance",
    ca = lambda instance:
        instance.transition.title + u" peticions de traducció",
    es = lambda instance:
        instance.transition.title + u" peticiones de traducción",
    en = lambda instance:
        instance.transition.title + u" translation requests"
)

translations.define(
    "woost.extensions.translationworkflow."
    "TranslationWorkflowTransitionView.transition_explanation",
    ca = u"Es canviarà l'estat de les següents peticions:",
    es = u"Se cambiará el estado de las peticiones siguientes:",
    en = u"The state of the following requests will be changed:"
)

translations.define(
    "woost.extensions.translationworkflow.assign_translator_schema.translator",
    ca = u"Traductor",
    es = u"Traductor",
    en = u"Translator"
)

# TranslationWorkflowTransitionPermission
#------------------------------------------------------------------------------
translations.define("TranslationWorkflowTransitionPermission",
    ca = u"Permís de transició del circuït de traduccions",
    es = u"Permiso de transición del circuito de traducciones",
    en = u"Translation workflow transition permission"
)

translations.define("TranslationWorkflowTransitionPermission-plural",
    ca = u"Permisos de transició del circuït de traduccions",
    es = u"Permisos de transición del circuito de traducciones",
    en = u"Translation workflow transition permissions"
)

translations.define(
    "woost.extensions.translationworkflow.transitionpermission."
    "TranslationWorkflowTransitionPermission-instance",
    ca = content_permission_translation_factory(
        "ca",
        lambda permission, subject, **kwargs:
            u"aplicar " + (
                join(
                    translations(transition)
                    for transition in permission.transitions
                )
                if permission.transitions else u"canvis d'estat"
            )
            + u" sobre peticions de traducció per " + subject
    ),
    es = content_permission_translation_factory(
        "es",
        lambda permission, subject, **kwargs:
            u"aplicar " + (
                join(
                    translations(transition)
                    for transition in permission.transitions
                )
                if permission.transitions else u"cambios de estado"
            )
            + u" sobre peticiones de traducción para " + subject
    ),
    en = content_permission_translation_factory(
        "en",
        lambda permission, subject, **kwargs:
            u"apply " + (
                join(
                    translations(transition)
                    for transition in permission.transitions
                )
                if permission.transitions else u"state changes"
            )
            + u" to translation requests for " + subject
    )
)

# TranslationWorkflowComment
#------------------------------------------------------------------------------
translations.define("TranslationWorkflowComment",
    ca = u"Comentari de petició de traducció",
    es = u"Comentario de petición de traducción",
    en = u"Translation request comment"
)

translations.define("TranslationWorkflowComment-plural",
    ca = u"Comentaris de petició de traducció",
    es = u"Comentarios de petición de traducción",
    en = u"Translation request comments"
)

translations.define("TranslationWorkflowComment.request",
    ca = u"Petició",
    es = u"Petición",
    en = u"Request"
)

translations.define("TranslationWorkflowComment.text",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

# TranslationWorkflowTable
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.translationworkflow.TranslationWorkflowTable."
    "missing_translation_notice",
    ca = u"Pendent de traduïr",
    es = u"Pendiente de traducción",
    en = u"Not translated yet"
)

# TranslationWorkflowRequestCard
#------------------------------------------------------------------------------
translations.define(
    "woost.views.TranslationWorkflowRequestCard."
    "translation_workflow_request_assigned_translator_label",
    ca = lambda translator:
        "" if translator is None
        else u"assignada a " + translations(translator),
    es = lambda translator:
        "" if translator is None
        else u"asignada a " + translations(translator),
    en = lambda translator:
        "" if translator is None
        else u"assigned to " + translations(translator)
)

# TranslationWorkflowChangesSummary
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.translationworkflow.TranslationWorkflowChangesSummary."
    "explanation",
    ca = u"Efecte sobre el circuït de traducció:",
    es = u"Efecto sobre el circuito de traducción:",
    en = u"Translation workflow effects:"
)

translations.define(
    "woost.extensions.translationworkflow.TranslationWorkflowChangesSummary."
    "entry.request_change_label-created",
    ca = u"Nova petició",
    es = u"Nueva petición",
    en = u"New request"
)

translations.define(
    "woost.extensions.translationworkflow.TranslationWorkflowChangesSummary."
    "entry.request_change_label-invalidated",
    ca = u"Petició invalidada",
    es = u"Petición invalidada",
    en = u"Invalidated request"
)

translations.define(
    "woost.extensions.translationworkflow.TranslationWorkflowChangesSummary."
    "entry.request_change_label-silenced",
    ca = u"Cap (petició silenciada)",
    es = u"Ninguno (petición silenciada)",
    en = u"None (silenced request)"
)

