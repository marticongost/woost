#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.translations import translations
from cocktail.translations.helpers import ca_possessive, plural2
from cocktail import schema
from collections import OrderedDict

translations.define("logged in as",
    ca = lambda user: u"Estàs identificat com a " \
            "<strong>%s</strong>" % translations(user, "ca"),
    es = lambda user: u"Estás identificado como " \
            "<strong>%s</strong>" % translations(user, "es"),
    en = lambda user: u"Logged in as "
            "<strong>%s</strong>" % translations(user, "en")
)

translations.define("Logout",
    ca = u"Sortir",
    es = u"Salir",
    en = u"Log out",
    fr = u"Log out"
)

translations.define("Type",
    ca = u"Tipus",
    es = u"Tipo",
    en = u"Type"
)

translations.define("Action new",
    ca = u"Nou",
    es = u"Nuevo",
    en = u"New"
)

translations.define("cocktail.html.shortcuts action new",
    ca = u"n",
    es = u"n",
    en = u"n"
)

translations.define("Action show_detail",
    ca = u"Veure resum",
    es = u"Ver resumen",
    en = u"Show detail"
)

translations.define("cocktail.html.shortcuts action show_detail",
    ca = u"v",
    es = u"v",
    en = u"w"
)

translations.define("Action edit",
    ca = u"Editar",
    es = u"Editar",
    en = u"Edit"
)

translations.define("cocktail.html.shortcuts action edit",
    ca = u"e",
    es = u"e",
    en = u"e"
)

translations.define("Action order",
    ca = u"Ordenar",
    es = u"Ordenar",
    en = u"Order"
)

translations.define("cocktail.html.shortcuts action order",
    ca = u"o",
    es = u"o",
    en = u"o"
)

translations.define("Action move",
    ca = u"Moure",
    es = u"Mover",
    en = u"Move"
)

translations.define("Action delete",
    ca = u"Eliminar",
    es = u"Eliminar",
    en = u"Delete"
)

translations.define("cocktail.html.shortcuts action delete",
    ca = u"i",
    es = u"i",
    en = u"d"
)

translations.define("Action changelog",
    ca = u"Històric",
    es = u"Histórico",
    en = u"Changelog"
)

translations.define("Action add",
    ca = u"Afegir",
    es = u"Añadir",
    en = u"Add"
)

translations.define("cocktail.html.shortcuts action add",
    ca = u"a",
    es = u"a",
    en = u"a"
)

translations.define("Action add_integral",
    ca = u"Afegir",
    es = u"Añadir",
    en = u"Add"
)

translations.define("cocktail.html.shortcuts action add_integral",
    ca = u"a",
    es = u"a",
    en = u"a"
)

translations.define("Action remove",
    ca = u"Treure",
    es = u"Quitar",
    en = u"Remove"
)

translations.define("cocktail.html.shortcuts action remove",
    ca = u"r",
    es = u"r",
    en = u"r"
)

translations.define("Action diff",
    ca = u"Veure canvis",
    es = u"Ver cambios",
    en = u"Show changes"
)

translations.define("cocktail.html.shortcuts action diff",
    ca = u"c",
    es = u"c",
    en = u"c"
)

translations.define("Action preview",
    ca = u"Vista prèvia",
    es = u"Vista previa",
    en = u"Preview"
)

translations.define("cocktail.html.shortcuts action preview",
    ca = u"p",
    es = u"p",
    en = u"p"
)

translations.define("Action open_resource",
    ca = u"Veure publicat",
    es = u"Ver publicado",
    en = u"Show published"
)

translations.define("cocktail.html.shortcuts action open_resource",
    ca = u"b",
    es = u"b",
    en = u"b"
)

translations.define("Action upload_files",
    ca = u"Importar fitxers",
    es = u"Importar ficheros",
    en = u"Import files"
)

translations.define("Action export_xls",
    ca = u"Exportar a MS Excel",
    es = u"Exportar a MS Excel",
    en = u"Export to MS Excel"
)

translations.define("Action save",
    ca = u"Desar",
    es = u"Guardar",
    en = u"Save"
)

translations.define("cocktail.html.shortcuts action save",
    ca = u"s",
    es = u"g",
    en = u"s"
)

translations.define("Action save_draft",
    ca = u"Desar esborrany",
    es = u"Guardar borrador",
    en = u"Save draft"
)

translations.define("Action confirm_draft",
    ca = u"Confirmar esborrany",
    es = u"Confirmar borrador",
    en = u"Confirm draft"
)

translations.define("Action discard_draft",
    ca = u"Descartar esborrany",
    es = u"Descartar borrador",
    en = u"Discard draft"
)

translations.define("Action select",
    ca = u"Seleccionar",
    es = u"Seleccionar",
    en = u"Select"
)

translations.define("cocktail.html.shortcuts action select",
    ca = u"s",
    es = u"s",
    en = u"s"
)

translations.define("Action close",
    ca = u"Tancar",
    es = u"Cerrar",
    en = u"Close"
)

translations.define("cocktail.html.shortcuts action close",
    ca = u"c",
    es = u"c",
    en = u"c"
)

translations.define("Action cancel",
    ca = u"Cancelar",
    es = u"Cancelar",
    en = u"Cancel"
)

translations.define("cocktail.html.shortcuts action cancel",
    ca = u"c",
    es = u"c",
    en = u"c"
)

translations.define("Action print",
    ca = u"Imprimir",
    es = u"Imprimir",
    en = u"Print"
)

translations.define("cocktail.html.shortcuts action print",
    ca = u"i",
    es = u"i",
    en = u"i"
)

translations.define("editing",
    ca = lambda item:
        u"Editant %s <em>'%s'</em>"
        % (translations(item.__class__.name, "ca").lower(),
           translations(item, "ca")),
    es = lambda item:
        u"Editando %s <em>'%s'</em>"
        % (translations(item.__class__.name, "es").lower(),
           translations(item, "es")),
    en = lambda item:
        u"Editing %s <em>'%s'</em>"
        % (translations(item.__class__.name, "es").lower(),
           translations(item, "es"))
)

translations.define("creating",
    ca = lambda content_type:
        u"Creant %s" % translations(content_type.__name__, "ca").lower(),
    es = lambda content_type:
        u"Creando %s" % translations(content_type.__name__, "es").lower(),
    en = lambda content_type:
        u"Creating new %s" % translations(content_type.__name__, "en").lower()
)

translations.define("woost.views.BackOfficeLayout edit stack select",
    ca = lambda type = None, relation = None:
        u"Seleccionar %s"
        % translations(relation if relation else type.name).lower(),
    es = lambda type = None, relation = None:
        u"Seleccionar %s"
        % translations(relation if relation else type.name).lower(),
    en = lambda type = None, relation = None:
        u"Select %s"
        % translations(relation if relation else type.name).lower()
)

translations.define("woost.views.BackOfficeLayout edit stack add",
    ca = lambda relation: u"Afegir %s" % translations(relation).lower(),
    es = lambda relation: u"Añadir %s" % translations(relation).lower(),
    en = lambda relation: u"Add %s" % translations(relation).lower()
)

translations.define("Backout",
    ca = u"Desfer",
    es = u"Deshacer",
    en = u"Backout"
)

translations.define("woost.views.BackOfficeShowDetailView revert",
    ca = u"Desfer",
    es = u"Deshacer",
    en = u"Undo"
)

translations.define("Discard changes",
    ca = u"Descartar",
    es = u"Descartar",
    en = u"Discard"
)

translations.define("Forget",
    ca = u"Oblidar",
    es = u"Olvidar",
    en = u"Forget"
)

translations.define("woost.views.ContentTable sort ascending",
    ca = u"Ordre ascendent",
    es = u"Orden ascendente",
    en = u"Ascending order"
)

translations.define("woost.views.ContentTable sort descending",
    ca = u"Ordre descendent",
    es = u"Orden descendente",
    en = u"Descending order"
)

translations.define("woost.views.ContentTable add column filter",
    ca = u"Afegir un filtre",
    es = u"Añadir un filtro",
    en = u"Add a filter"
)

translations.define("BackOfficeContentView.element",
    ca = u"Element",
    es = u"Elemento",
    en = u"Item"
)

translations.define("woost.views.ContentView content type",
    ca = u"Tipus:",
    es = u"Tipo:",
    en = u"Type:"
)

translations.define("BackOfficeContentView.class",
    ca = u"Tipus",
    es = u"Tipo",
    en = u"Type"
)

translations.define("woost.views.BackOfficeContentView user views",
    ca = u"Vistes freqüents:",
    es = u"Vistas frecuentes:",
    en = u"Bookmarks:"
)

translations.define("woost.views.BackOfficeContentView add user view",
    ca = u"Crear vista",
    es = u"Crear vista",
    en = u"New view"
)

translations.define("ContentView search",
    ca = u"Cercar",
    es = u"Buscar",
    en = u"Search"
)

translations.define("woost.views.ContentView label",
    ca = u"Veure com:",
    es = u"Ver como:",
    en = u"See as:"
)

translations.define("woost.views.ContentView show advanced search",
    ca = u"Més opcions de cerca",
    es = u"Mas opciones de búsqueda",
    en = u"More search options"
)

translations.define("woost.views.ContentView close advanced search",
    ca = u"Descartar la cerca",
    es = u"Descartar la búsqueda",
    en = u"Discard search"
)

translations.define("woost.views.ContentView search button",
    ca = u"Cercar",
    es = u"Buscar",
    en = u"Search"
)

translations.define("Advanced search",
    ca = u"Cerca avançada",
    es = u"Búsqueda avanzada",
    en = u"Advanced search"
)

translations.define("woost.views.TreeContentView expansion controls",
    ca = u"Arbre:",
    es = u"Árbol:",
    en = u"Tree:"
)

translations.define("woost.views.TreeContentView expand all",
    ca = u"Desplegar",
    es = u"Expandir",
    en = u"Unfold"
)

translations.define("woost.views.TreeContentView collapse all",
    ca = u"Plegar",
    es = u"Contraer",
    en = u"Fold"
)

translations.define("woost.models.Item draft copy",
    ca = lambda item, draft_id, **kwargs: u"Borrador %d %s"
        % (draft_id, ca_possessive(translations(item, "ca"))),
    es = lambda item, draft_id, **kwargs: u"Borrador %d de %s"
        % (draft_id, translations(item, "es")),
    en = lambda item, draft_id, **kwargs: u"Draft %d for %s"
        % (draft_id, translations(item, "en"))
)

translations.define("woost.views.ContentTable draft label",
    ca = "Esborrany %(draft_id)d",
    es = "Borrador %(draft_id)d",
    en = "Draft %(draft_id)d"
)

translations.define("Differences for",
    ca = lambda item: u"Canvis a <em>'%s'</em>" % translations(item, "ca"),
    es = lambda item: u"Cambios en <em>'%s'</em>" % translations(item, "es"),
    en = lambda item: u"Changes in <em>'%s'</em>" % translations(item, "en")
)

translations.define("No differences",
    ca = u"L'element no té cap canvi.",
    es = u"El elemento no tiene ningún cambio.",
    en = u"The item has no changes."
)

translations.define("woost.views.BackOfficeDiffView member",
    ca = u"Membre",
    es = u"Miembro",
    en = u"Member"
)

translations.define("woost.views.BackOfficeDiffView previous value",
    ca = u"Valor anterior",
    es = u"Valor anterior",
    en = u"Previous value"
)

translations.define("woost.views.BackOfficeDiffView new value",
    ca = u"Valor nou",
    es = u"Valor nuevo",
    en = u"New value"
)

translations.define("Action revert",
    ca = u"Desfer",
    es = u"Deshacer",
    en = u"Undo"
)

translations.define("Editing draft",
    ca = u"Estàs editant un nou esborrany. L'element no esdevindrà actiu fins "
         u"que no el confirmis.",
    es = u"Estás editando un nuevo borrador. El elemento no se activará hasta "
         u"que no lo confirmes.",
    en = u"You are editing a new draft. The element won't become active until "
         u"you confirm it."
)

translations.define("Editing draft copy",
    ca = u"Estàs editant un esborrany d'un <a href='%(location)s'>element</a>."
         u" Els canvis no es veuran reflectits a l'original fins que no "
         u"confirmis l'esborrany.",
    es = u"Estás editando un borrador de un <a href='%(location)s'>"
         u"elemento</a>. Tus cambios no se verán reflejados en el original "
         u"hasta que no confirmes el borrador.",
    en = u"You are editing a draft of an <a href='%(location)s'>item</a>. "
         u"Your changes won't be made permanent until you confirm the draft."
)

translations.define("Draft source reference",
    ca = u"Pots accedir a la còpia original de l'element "
         u"<a href='%(location)s'>aquí</a>.",
    es = u"Puedes acceder a la copia original del elemento "
         u"<a href='%(location)s'>aquí</a>.",
    en = u"The original copy of the item can be found "
         u"<a href='%(location)s'>here</a>."
)

translations.define("woost.views.ActionBar Additional actions",
    ca = u"Més accions",
    es = u"Más acciones",
    en = u"More actions"
)

translations.define("datetime format",
    ca = "%d/%m/%Y %H:%M",
    es = "%d/%m/%Y %H:%M",
    en = "%Y-%m-%d %H:%M"
)

translations.define("BackOfficeOrderView last position",
    ca = u"-- Final de la llista --",
    es = u"-- Final de la lista --",
    en = u"-- End of the list --"
)

translations.define("woost.views.BackOfficeOrderView.stack_node_description",
    ca = u"ordenar",
    es = u"ordenar",
    en = u"rearrange"
)

translations.define(
    "woost.views.BackOfficeOrderView.insertion_point_explanation",
    ca = u"Els elements seleccionats es situaran <em>davant</em> del punt "
        u"indicat:",
    es = u"Los elementos seleccionados se situarán <em>delate</em> del punto "
        u"indicado:",
    en = u"The selected items will be inserted <em>before</em> the specified "
        u"point:"
)

translations.define(
    "woost.controllers.backoffice.movecontroller.TreeCycleError-instance",
    ca = u"No es pot inserir un element dins de sí mateix.",
    es = u"No se puede insertar un elemento dentro de si mismo.",
    en = u"Can't insert an element into itself."
)

translations.define(
    "woost.controllers.backoffice.DragAndDropController.drop_notification",
    ca = lambda dragged_object, target_object, target_member:
        (
            u"S'ha establert %s com a %s %s" 
            if isinstance(target_member, schema.Reference)
            else u"S'ha afegit %s a %s %s"
        ) % (
            translations(dragged_object),
            translations(target_member),
            ca_possessive(translations(target_object))
        ),
    es = lambda dragged_object, target_object, target_member:
        (
            u"Se ha establecido %s como %s de %s"
            if isinstance(target_member, schema.Reference)
            else u"Se ha añadido %s a %s de %s"
        ) % (
            translations(dragged_object),
            translations(target_member),
            translations(target_object)
        ),
    en = lambda dragged_object, target_object, target_member:
        (
            u"%s set as %s of %s"
            if isinstance(target_member, schema.Reference)
            else u"%s added to the %s of %s"
        ) % (
            translations(dragged_object),
            translations(target_member),
            translations(target_object)
        )
)

translations.define("woost.views.BackOfficeLayout.drop",
    ca = u"Inserir a dins",
    es = u"Insertar dentro",
    en = u"Insert inside"
)

translations.define("woost.views.BackOfficeLayout.drop_before",
    ca = u"Inserir davant",
    es = u"Insertar en frente",
    en = u"Insert before"
)

translations.define("woost.views.BackOfficeLayout.drop_after",
    ca = u"Inserir darrere",
    es = u"Insertar detrás",
    en = u"Insert after"
)

def _selection_error_ca(instance):    
    if instance.action.min and instance.selection_size < instance.action.min:
        bound = instance.action.min
        bound_label = "mínim"
    else:
        bound = instance.action.max
        bound_label = "màxim"

    return u"No es pot %s una selecció %s; el %s és %s" % (
        translations(instance.action).lower(),
        plural2(
            instance.selection_size, 
            "d'un sol element", 
            "de %d elements" % instance.selection_size
        ),
        bound_label,
        plural2(
            bound,
            "d'un element",
            "de %d elements" % bound
        )
    )

def _selection_error_es(instance):    
    if instance.action.min and instance.selection_size < instance.action.min:
        bound = instance.action.min
        bound_label = "mínimo"
    else:
        bound = instance.action.max
        bound_label = "máximo"

    return u"No se puede %s una selección de %s; el %s es de %s" % (
        translations(instance.action).lower(),
        plural2(
            instance.selection_size, 
            "a single element", 
            "%d elements" % instance.selection_size
        ),
        bound_label,
        plural2(
            bound,
            "un elemento",
            "%d elementos" % bound
        )
    )

def _selection_error_en(instance):    
    if instance.action.min and instance.selection_size < instance.action.min:
        bound = instance.action.min
        bound_label = "at least"
    else:
        bound = instance.action.max
        bound_label = "no more than"

    return u"Can't %s a selection consisting of %s; must select %s %s" % (
        translations(instance.action).lower(),
        plural2(
            instance.selection_size, 
            "a single element", 
            "%d elements" % instance.selection_size
        ),
        bound_label,
        plural2(
            bound,
            "one element",
            "%d elements" % bound
        )
    )

translations.define(
    "woost.controllers.backoffice.useractions.SelectionError-instance",
    ca = _selection_error_ca,
    es = _selection_error_es,
    en = _selection_error_en
)

translations.define(
    "woost.controllers.backoffice.editstack.WrongEditStackError-instance",
    ca = u"La sessió d'edició indicada no existeix o ha expirat.",
    es = u"La sesión de edición indicada no existe o ha expirado.",
    en = u"The indicated edit session doesn't exist, or has expired."
)


translations.define(
    "woost.controllers.backoffice.fileeditnode.FileRequiredError-instance",
    ca = u"S'ha de carregar un fitxer o seleccionar un fitxer local",
    es = u"Debe subirse un fichero o seleccionar un fichero local",
    en = u"Must upload a file, or select a local file"
)

translations.define(
    "forbidden value",
    ca = u"Camp restringit",
    es = u"Campo restringido",
    en = u"Restricted field"
)

translations.define("woost.views.BackOfficeDeleteView.warning",
    ca = u"S'eliminaran els elements indicats:",
    es = u"Se eliminarán los elementos indicados:",
    en = u"The following elements will be deleted:"
)

translations.define("woost.views.BackOfficeDeleteView.block_notice",
    ca = u"No es pot completar l'eliminació, ja que alguns dels elements  "
         u"seleccionats tenen contingut relacionat que impedeix que puguin "
         u"ser eliminats:",
    es = u"No se puede completar la eliminación, ya que algunos de los "
         u"elementos seleccionados contienen vinculaciones que impiden que "
         u"puedan ser eliminados:",
    en = u"The delete operation could not be executed; it is blocked by the "
         u"the following relations:"
)

translations.define("woost.views.BackOfficeDeleteView.cascade_details",
    ca = u"També eliminarà:",
    es = u"También eliminará:",
    en = u"Will also delete:"
)

translations.define("woost.views.BackOfficeDeleteView.block_details",
    ca = u"Bloquejat per:",
    es = u"Bloqueado por:",
    en = u"Blocked by:"
)

translations.define("woost.views.BackOfficeDeleteView.confirm_delete_button",
    ca = u"Eliminar",
    es = u"Eliminar",
    en = u"Delete"
)

translations.define("woost.views.BackOfficeDeleteView.cancel_button",
    ca = u"Cancel·lar",
    es = u"Cancelar",
    en = u"Cancel"
)

translations.define("woost.views.ItemSelector select",
    ca = u"Seleccionar",
    es = u"Seleccionar",
    en = u"Select"
)

translations.define("woost.views.ItemSelector unlink",
    ca = u"Desvincular",
    es = u"Desvincular",
    en = u"Unlink"
)

translations.define("woost.views.ItemSelector new",
    ca = u"Nou",
    es = u"Nuevo",
    en = u"New"
)

translations.define("woost.views.ItemSelector edit",
    ca = u"Editar",
    es = u"Editar",
    en = u"Edit"
)

translations.define("woost.views.ItemSelector delete",
    ca = u"Eliminar",
    es = u"Eliminar",
    en = u"Delete"
)

translations.define("woost.views.BackOfficeItemSelectorView title", 
    ca = lambda type: "Seleccionar " + translations(type.name, "ca").lower(),
    es = lambda type: "Seleccionar " + translations(type.name, "es").lower(),
    en = lambda type: "Select " + translations(type.name, "en").lower()
)

translations.define("woost.views.BackOfficeShowDetailView open resource",
    ca = u"Obrir el fitxer",
    es = u"Abrir el fichero",
    en = u"Show file"
)

translations.define(
    "woost.models.userfilter.OwnItemsFilter-instance",
    ca = u"Elements propis",
    es = u"Elementos propios",
    en = u"Owned items"
)

translations.define(
    "woost.models.userfilter.IsPublishedFilter-instance",
    ca = u"Elements publicats",
    es = u"Elementos publicados",
    en = u"Published elements"
)

translations.define("woost.models.userfilter.TypeFilter-instance",
    ca = u"Tipus",
    es = u"Tipo",
    en = u"Type"
)

translations.define("UserFilter.is_inherited",
    ca = u"Inclou fills",
    es = u"Incluye hijos",
    en = u"Children included"
)

translations.define("Changelog.action",
    ca = u"Acció",
    es = u"Acción",
    en = u"Action"
)

translations.define("Changelog.changes",
    ca = u"Elements",
    es = u"Elementos",
    en = u"Items"
)

translations.define("woost.views.BackOfficeChangeLogView title",
    ca = u"Històric",
    es = u"Histórico",
    en = u"Changelog"
)

translations.define("woost.views.BackOfficeChangeLogView collapsed",
    ca = u"%(count)s elements",
    es = u"%(count)s elementos",
    en = u"%(count)s items"
)

translations.define("woost.views.BackOfficeChangeLogView expanded",
    ca = u"Tornar a ocultar",
    es = u"Volver a ocultar",
    en = u"Fold"
)

# woost.views.EditLink
#------------------------------------------------------------------------------
translations.define("woost.views.EditLink-publishable_target",
    ca = u"aquesta pàgina",
    es = u"esta página",
    en = u"this page"
)

translations.define("woost.views.EditLink-site",
    ca = u"les propietats del lloc web",
    es = u"las propiedades del sitio web",
    en = u"site-wide properties"
)

translations.define("woost.views.EditLink-create",
    ca = lambda target_desc = None:
        u"Crear " + (target_desc or u"element"),
    es = lambda target_desc = None:
        u"Crear " + (target_desc or u"elemento"),
    en = lambda target_desc = None:
        u"Create " + (target_desc or u"element")
)

translations.define("woost.views.EditLink-modify",
    ca = lambda target_desc = None:
        u"Editar " + (target_desc or u"això"),
    es = lambda target_desc = None:
        u"Editar " + (target_desc or u"esto"),
    en = lambda target_desc = None:
        u"Edit " + (target_desc or u"this")
)

translations.define("woost.views.EditLink-delete",
    ca = lambda target_desc = None:
        u"Eliminar " + (target_desc or u"això"),
    es = lambda target_desc = None:
        u"Eliminar " + (target_desc or u"esto"),
    en = lambda target_desc = None:
        u"Delete " + (target_desc or u"this")
)

# Initialization content
#------------------------------------------------------------------------------
translations.define(
    "woost.models.initialization Administrators role title",
    ca = u"Administradors",
    es = u"Administradores",
    en = u"Administrators"
)

translations.define(
    "woost.models.initialization Anonymous role title",
    ca = u"Anònim",
    es = u"Anónimo",
    en = u"Anonymous"
)

translations.define(
    "woost.models.initialization Everybody role title",
    ca = u"Tothom",
    es = u"Todos los usuarios",
    en = u"Everybody"
)

translations.define(
    "woost.models.initialization Authenticated role title",
    ca = u"Autenticat",
    es = u"Autenticado",
    en = u"Authenticated"
)

translations.define(
    "woost.models.initialization Back office title",
    ca = u"Gestor de continguts",
    es = u"Gestor de contenidos",
    en = u"Content Manager"
)

translations.define(
    "woost.models.initialization Standard template title",
    ca = u"Plantilla estàndard",
    es = u"Plantilla estándar",
    en = u"Standard template"
)

translations.define(
    "woost.models.initialization Login Form template title",
    ca = u"Plantilla formulario de autenticació d'usuari",
    es = u"Plantilla formulario de autenticación de usuario",
    en = u"Login form template"
)

translations.define(
    "woost.models.initialization Password Change Request template title",
    ca = u"Plantilla sol·licitud de canvi de contrasenya",
    es = u"Plantilla solicitud de cambio de contraseña",
    en = u"Password change request template"
)

translations.define(
    "woost.models.initialization Password Change Confirmation Email template title",
    ca = u"Plantilla de correu electrònic per sol·licitar el canvi de contrasenya",
    es = u"Plantilla de correo electrónico para solicitud de cambio de contraseña",
    en = u"Password change confirmation email template"
)

translations.define(
    "woost.models.initialization Password Change Confirmation Email subject",
    ca = u"Canvi de contrasenya",
    es = u"Cambio de contraseña",
    en = u"Password change"
)

translations.define(
    "woost.models.initialization Password Change Confirmation Email body",
    ca = u"""Hola ${user.email}: <br/><br/>
        Fes clic en el següent enllaç per establir la teva nova contrasenya:<br/>
        <a href='${confirmation_url}'>${confirmation_url}</a>""",
    es = u"""Hola ${user.email}: <br/><br/>
        Haz clic en el siguiente enlace para establecer tu nueva contraseña:<br/>
        <a href='${confirmation_url}'>${confirmation_url}</a>""",
    en = u"""Hello ${user.email}, <br/><br/>
        Click on the following link to set your new password:<br/>
        <a href='${confirmation_url}'> ${confirmation_url}</a>"""
)

translations.define(
    "woost.models.initialization Password Change Confirmation view title",
    ca = u"Plantilla formulari de canvi de contrasenya",
    es = u"Plantilla formulario de cambio de contraseña",
    en = u"Password change form template"
)

translations.define(
    "woost.models.initialization Password Change Confirmation page title",
    ca = u"Pàgina de confirmació de canvi de contrasenya",
    es = u"Página de confirmación de cambio de contraseña",
    en = u"Password change confirmation page"
)

translations.define(
    "woost.models.initialization Password Change Confirmation page body",
    ca = u"Introduïx la nova contrasenya per la teva compte d'usuari",
    es = u"Introduce tu nueva contraseña para tu cuenta de usuario",
    en = u"Enter the new password for your user account"
)

translations.define(
    "woost.models.initialization Site style sheet title",
    ca = u"Full d'estils global",
    es = u"Hoja de estilos global",
    en = u"Global stylesheet"
)

translations.define(
    "woost.models.initialization Home page title",
    ca = u"Lloc web",
    es = u"Sitio web",
    en = u"Web site"
)

translations.define(
    "woost.models.initialization Home page inner title",
    ca = u"Benvingut!",
    es = u"Bienvenido!",
    en = u"Welcome!"
)

translations.define(
    "woost.models.initialization Home page body",
    ca = u"<p>El teu lloc web s'ha creat correctament. Ja pots començar "
        u"a <a href='%(uri)s'>treballar-hi</a> i substituir aquesta pàgina "
        u"amb els teus propis continguts.</p>",
    es = u"<p>Tu sitio web se ha creado correctamente. Ya puedes empezar "
        u"a <a href='%(uri)s'>trabajar</a> en él y sustituir esta página "
        u"con tus propios contenidos.</p>",
    en = u"<p>Your web site has been created successfully. You can start "
        u"<a href='%(uri)s'>working on it</a> and replace this page with "
        u"your own content.</p>"
)

translations.define(
    "woost.models.initialization Not found error page title",
    ca = u"Pàgina no trobada",
    es = u"Página no encontrada",
    en = u"Page not found"
)

translations.define(
    "woost.models.initialization Not found error page body",
    ca = u"<p>La direcció indicada no coincideix amb cap dels continguts "
         u"del web. Si us plau, revísa-la i torna-ho a provar.</p>",
    es = u"<p>La dirección indicada no coincide con ninguno de los "
         u"contenidos del web. Por favor, revísala y inténtalo de nuevo.</p>",
    en = u"<p>Couldn't find the indicated address. Please, verify it and try "
         u"again.</p>"
)

translations.define(
    "woost.models.initialization Login page title",
    ca = u"Autenticació d'usuari",
    es = u"Autenticación de usuario",
    en = u"User authentication"
)

translations.define(
    "woost.controllers.authentication.AuthenticationFailedError-instance",
    ca = u"Usuari o contrasenya incorrectes",
    es = u"Usuario o contraseña incorrectos",
    en = u"Incorrect user or password"
)

translations.define(
    "woost.models.initialization Password Change page title",
    ca = u"Canvi de contrasenya d'usuari",
    es = u"Cambio de contraseña de usuario",
    en = u"Password change"
)

translations.define(
    "woost.models.initialization Password Change page body",
    ca = u"<p>Introdueix el teu identificador d'usuari per iniciar el "
         u"procés de canvi de contrasenya</p>",
    es = u"<p>Introduce a tu identificador de usuario para iniciar el "
         u"proceso de cambio de contraseña</p>",
    en = u"<p>Enter your user identifier below to start the password "
         u"change process</p>"""
)

translations.define(
    "woost.models.initialization Forbidden error page title",
    ca = u"Accés denegat",
    es = u"Acceso denegado",
    en = u"Forbidden"
)

translations.define(
    "woost.models.initialization Forbidden error page body",
    ca = u"<p>No es permet l'accés a aquesta secció del web.</p>",
    es = u"<p>No se permite el acceso a esta sección del sitio.</p>",
    en = u"<p>Access denied.</p>"
)

translations.define(
    "woost.models.initialization Create action title",
    ca = u"Crear",
    es = u"Crear",
    en = u"Create"
)

translations.define(
    "woost.models.initialization Read action title",
    ca = u"Veure",
    es = u"Ver",
    en = u"Read"
)

translations.define(
    "woost.models.initialization Modify action title",
    ca = u"Modificar",
    es = u"Modificar",
    en = u"Modify"
)

translations.define(
    "woost.models.initialization Delete action title",
    ca = u"Eliminar",
    es = u"Eliminar",
    en = u"Delete"
)

translations.define(
    "woost.models.initialization Confirm draft action title",
    ca = u"Confirmar esborrany",
    es = u"Confirmar borrador",
    en = u"Confirm draft"
)

translations.define(
    "woost.models.initialization Page tree user view",
    ca = u"Arbre de pàgines",
    es = u"Árbol de páginas",
    en = u"Page tree"
)

translations.define(
    "woost.models.initialization Own items user view",
    ca = u"Els meus elements",
    es = u"Mis elementos",
    en = u"My items"
)

translations.define(
    "woost.models.initialization File gallery user view",
    ca = u"Galeria de fitxers",
    es = u"Galería de ficheros",
    en = u"File gallery"
)

translations.define("woost.models.initialization Document controller title",
    ca = u"Controlador de document",
    es = u"Controlador de documento",
    en = u"Document controller"
)

translations.define("woost.models.initialization File controller title",
    ca = u"Controlador de fitxer",
    es = u"Controlador de fichero",
    en = u"File controller"
)

translations.define("woost.models.initialization URI controller title",
    ca = u"Controlador de redirecció",
    es = u"Controlador de redirección",
    en = u"Redirection controller"
)

translations.define("woost.models.initialization Styles controller title",
    ca = u"Controlador d'estils d'usuari",
    es = u"Controlador de estilos de usuario",
    en = u"User styles controller"
)

translations.define("woost.models.initialization Feed controller title",
    ca = u"Controlador de sindicació de continguts",
    es = u"Controlador de sindicación de contenidos",
    en = u"Feed controller"
)

translations.define("woost.models.initialization BackOffice controller title",
    ca = u"Controlador de panell administratiu",
    es = u"Controlador de panel administrativo",
    en = u"Backoffice controller"
)

translations.define("woost.models.initialization WebServices controller title",
    ca = u"Controlador de serveis web",
    es = u"Controlador de servicios web",
    en = u"Web services controller"
)

translations.define("woost.models.initialization FirstChildRedirection controller title",
    ca = u"Controlador de redirecció automàtica al primer fill",
    es = u"Controlador de redirección automática al primer hijo",
    en = u"First child redirection controller"
)

translations.define("woost.models.initialization Login controller title",
    ca = u"Controlador de autenticació d'usuari",
    es = u"Controlador de autenticación de usuario",
    en = u"User authentication controller"
)

translations.define("woost.models.initialization PasswordChange controller title",
    ca = u"Controlador de canvi de contrasenya",
    es = u"Controlador de cambio de contraseña",
    en = u"Password change controller"
)

translations.define("woost.models.initialization PasswordChangeConfirmation controller title",
    ca = u"Controlador de confirmació de canvi de contrasenya",
    es = u"Controlador de confirmación de cambio de contraseña",
    en = u"Password change confirmation controller"
)

translations.define("woost.models.initialization User styles title",
    ca = u"Estils d'usuari",
    es = u"Estilos de usuario",
    en = u"User styles"
)

translations.define("woost.models.initialization Web services title",
    ca = u"Serveis web",
    es = u"Servicios web",
    en = u"Web services"
)

translations.define("woost.models.initialization delete_files_trigger",
    ca = u"Esborrar fitxers del disc quan s'elimini el seu element",
    es = u"Borrar ficheros del disco cuando se elimine su elemento",
    en = u"Erase files from disc when their item is deleted"
)

translations.define("woost.models.initialization content_renderer",
    ca = u"Imatge del contingut",
    es = u"Imagen del contenido",
    en = u"Content renderer"
)

translations.define("woost.models.initialization icon16_renderer",
    ca = u"Icones de 16x16",
    es = u"Iconos de 16x16",
    en = u"16x16 icons"
)

translations.define("woost.models.initialization icon32_renderer",
    ca = u"Icones de 32x32",
    es = u"Iconos de 32x32",
    en = u"32x32 icons"
)

translations.define("woost.models.initialization default_image_factory",
    ca = u"Imatge sense processar",
    es = u"Imagen sin procesar",
    en = u"Unprocessed image"
)

translations.define("woost.models.initialization icon16_image_factory",
    ca = u"Icona de 16x16",
    es = u"Icono de 16x16",
    en = u"16x16 icon"
)

translations.define("woost.models.initialization icon32_image_factory",
    ca = u"Icona de 32x32",
    es = u"Icono de 32x32",
    en = u"32x32 icon"
)

translations.define(
    "woost.models.initialization backoffice_thumbnail_image_factory",
    ca = u"Vista en miniatura del panell d'administració",
    es = u"Vista en miniatura del panel de administración",
    en = u"Backoffice thumbnail"
)

translations.define(
    "woost.models.initialization backoffice_small_thumbnail_image_factory",
    ca = u"Vista en miniatura petita del panell d'administració",
    es = u"Vista en miniatura pequeña del panel de administración",
    en = u"Backoffice small thumbnail"
)

translations.define(
    "woost.models.initialization image_gallery_close_up_image_factory",
    ca = u"Ampliació estàndard de la galeria d'imatges",
    es = u"Ampliación estándar de la galería de imágenes",
    en = u"Default image gallery close up"
)

translations.define(
    "woost.models.initialization image_gallery_thumbnail_image_factory",
    ca = u"Miniatura estàndard de la galeria d'imatges",
    es = u"Miniatura estándar de la galería de imágenes",
    en = u"Default image gallery thumbnail"
)

translations.define("woost.views.ContentTable sorting header",
    ca = u"Ordenació",
    es = u"Ordenación",
    en = u"Order"
)

translations.define("woost.views.ContentTable grouping header",
    ca = u"Agrupació",
    es = u"Agrupación",
    en = u"Grouping"
)

translations.define("woost.views.ContentTable search header",
    ca = u"Filtres",
    es = u"Filtros",
    en = u"Filters"
)

translations.define("woost.views.ImageGallery.close_button",
    ca = u"Tancar la imatge",
    es = u"Cerrar la imagen",
    en = u"Close image"
)

translations.define("woost.views.ImageGallery.next_button",
    ca = u"Següent",
    es = u"Siguiente",
    en = u"Next"
)

translations.define("woost.views.ImageGallery.previous_button",
    ca = u"Anterior",
    es = u"Anterior",
    en = u"Previous"
)

translations.define("woost.views.ImageGallery.loading_sign",
    ca = u"Carregant la imatge",
    es = u"Cargando la imagen",
    en = u"Loading image"
)

translations.define("woost.views.ImageGallery.original_image_link",
    ca = u"Descarregar l'original",
    es = u"Descargar el original",
    en = u"Download the original"
)

# Content views
#------------------------------------------------------------------------------
translations.define("View as",
    ca = u"Visualització",
    es = u"Visualización",
    en = u"View as"
)

translations.define("flat content view",
    ca = u"Veure com a llistat",
    es = u"Ver como listado",
    en = u"Show as listing"
)

translations.define("tree content view",
    ca = u"Veure com a arbre",
    es = u"Ver como árbol",
    en = u"Show as tree"
)

translations.define("thumbnails content view",
    ca = u"Veure com a miniatures",
    es = u"Ver como miniaturas",
    en = u"Show as thumbnails grid"
)

translations.define("calendar content view",
    ca = u"Veure com a calendari",
    es = u"Ver como calendario",
    en = u"Show as calendar"
)

translations.define("order content view",
    ca = u"Veure com a llista ordenable",
    es = u"Ver como lista ordenadable",
    en = u"Show as ordered listing"
)

translations.define("woost.views.CalendarContentView current year",
    ca = u"Any actual",
    es = u"Año actual",
    en = u"Current year"
)

translations.define("woost.views.CalendarContentView previous year",
    ca = u"Any anterior",
    es = u"Año anterior",
    en = u"Previous year"
)

translations.define("woost.views.CalendarContentView next year",
    ca = u"Any següent",
    es = u"Año siguiente",
    en = u"Next year"
)

translations.define("woost.views.CalendarContentView current month",
    ca = u"Mes actual",
    es = u"Mes actual",
    en = u"Current month"
)

translations.define("woost.views.CalendarContentView previous month",
    ca = u"Mes anterior",
    es = u"Mes anterior",
    en = u"Previous month"
)

translations.define("woost.views.CalendarContentView next month",
    ca = u"Mes següent",
    es = u"Mes siguiente",
    en = u"Next month"
)

translations.define("woost.views.CalendarContentView select year layout",
    ca = u"Vista de l'any",
    es = u"Vista del año",
    en = u"Year view"
)

translations.define(
    "woost.views.CalendarContentView ongoing items message",
    ca = u"Elements en curs:",
    es = u"Elementos en curso:",
    en = u"Ongoing items:"
)

# Edit form
#------------------------------------------------------------------------------
translations.define("BackOfficeEditForm.translations",
    ca = u"Traduccions",
    es = u"Traducciones",
    en = u"Translations"
)

translations.define("BackOfficeEditForm.properties",
    ca = u"Propietats",
    es = u"Propiedades",
    en = u"Properties"
)

translations.define("BackOfficeEditForm.relations",
    ca = u"Relacions",
    es = u"Relaciones",
    en = u"Relations"
)

translations.define("BackOfficeEditForm.change_password",
    ca = u"Canviar la contrasenya",
    es = u"Cambiar la contraseña",
    en = u"Change password"
)

translations.define("BackOfficeEditForm.password_confirmation",
    ca = u"Confirmar la contrasenya",
    es = u"Confirmar la contraseña",
    en = u"Confirm password"
)

translations.define(
    "woost.controllers.backoffice.usereditnode."
    "PasswordConfirmationError-instance",
    ca = u"Les contrasenyes no coincideixen",
    es = u"Las contraseñas no coinciden",
    en = u"Passwords don't match"
)

translations.define(
    "woost.views.BackOfficeEditView Changes saved",
    ca = lambda item, is_new:
        (
            u"S'ha creat l'element <strong>%s</strong>"
            if is_new
            else u"Canvis a <strong>%s</strong> desats"
        )
        % translations(item, "ca"),
    es = lambda item, is_new:
        (
            u"Se ha creado el elemento <strong>%s</strong>"
            if is_new
            else u"Cambios en <strong>%s</strong> guardados"
        )
        % translations(item, "es"),
    en = lambda item, is_new:
        (
            u"New item <strong>%s</strong> stored"
            if is_new
            else u"Saved changes to <strong>%s</strong>"
        )
        % translations(item, "en")
)

translations.define("woost.views.BackOfficeEditView Create another",
    ca = u"Crear un altre element",
    es = u"Crear otro elemento",
    en = u"Create another item"
)

translations.define(
    "woost.views.BackOfficeEditView Draft confirmed",
    ca = lambda item, is_new:
        (
            u"S'ha creat l'element <strong>%s</strong> a partir de l'esborrany"
            if is_new
            else u"Els canvis de l'esborrany s'han aplicat a "
                 u"<strong>%s</strong>"
        )
        % translations(item, "ca"),
    es = lambda item, is_new:
        (
            u"Se ha creado el elemento <strong>%s</strong> a partir del "
            u"borrador"
            if is_new
            else u"Se ha actualizado <strong>%s</strong> con los cambios del "
                 u"borrador"
        )
        % translations(item, "es"),
    en = lambda item, is_new:
        (
            u"Draft stored as new item <strong>%s</strong>"
            if is_new
            else u"Saved changes from draft to <strong>%s</strong>"
        )
        % translations(item, "en")
)

translations.define(
    "woost.views.BackOfficeItemView pending changes warning",
    ca = u"Hi ha canvis pendents de desar. Si abandones el formulari d'edició "
        u"els canvis es perdran.",
    es = u"Hay cambios pendientes de guardar. Si abandonas el formulario de "
        u"edición los cambios se perderán.",
    en = u"There are unsaved changes. If you navigate away from the edit form "
        u"your modifications will be lost."
)

translations.define(
    "woost.controllers.backoffice.basebackofficecontroller."
    "EditStateLostError",
    ca = u"La sessió d'edició en que estaves treballant s'ha perdut.",
    es = u"La sesión de edición en que estabas trabajando se ha perdido.",
    en = u"The edit session you were working on has been lost."
)

translations.define("woost.views.BaseView alternate language link",
    ca = lambda lang: u"Versió en " + translations(lang, "ca"),
    es = lambda lang: u"Versión en " + translations(lang, "es"),
    en = lambda lang: translations(lang, "en") + " version"
)

translations.define("woost.views.StandardView.navigation_title",
    ca = u"Menú principal",
    es = u"Menú principal",
    en = u"Main navigation"
)

translations.define("woost.views.StandardView attachment icon description",
    ca = u"Icona",
    es = u"Icono",
    en = u"Icon"
)

translations.define("woost.views.StandardView fallback language notice",
    ca = lambda fallback:
        u"Aquesta pàgina no es troba disponible en català. Et mostrem "
        u"la seva versió en %s." % translations(fallback).lower(),
    es = lambda fallback:
        u"Esta página no se encuentra disponible en español. Te "
        u"mostramos su versión en %s." % translations(fallback).lower(),
    en = lambda fallback:
        u"This page is not available in english. Its %s version is "
        u"shown instead." % translations(fallback).lower()
)

translations.define("woost.views.StandardView.phone_number",
    ca = u"Tel",
    es = u"Tel",
    en = u"Telephone"
)

translations.define("UploadFilesForm.upload",
    ca = u"Fitxer ZIP",
    es = u"Fichero ZIP",
    en = u"ZIP file"
)

translations.define(
    "UploadFilesForm.upload.mime_type-error: cocktail.schema.exceptions.EnumerationError",
    ca = u"El fitxer indicat no és un fitxer ZIP",
    es = u"El fichero indicado no es un fichero ZIP",
    en = u"The selected file is not a ZIP file"
)

translations.define("woost.views.BackOfficeUploadFilesView.success_notice",
    ca = lambda count: u"S'ha importat un total de <strong>%d</strong> %s:"
        % (count, plural2(count, u"fitxer", u"fitxers")),
    es = lambda count: u"Se han importado un total de <strong>%d</strong> %s:"
        % (count, plural2(count, u"fichero", u"ficheros")),
    en = lambda count: u"Uploaded <strong>%d</strong> %s:"
        % (count, plural2(count, u"file", u"files"))
)

translations.define("woost.views.BackOfficeUploadFilesView.upload_another",
    ca = u"Importar més fitxers",
    es = u"Importar más ficheros",
    en = u"Import more files"
)

# Item
#------------------------------------------------------------------------------
translations.define("Item",
    ca = u"Element genèric",
    es = u"Elemento genérico",
    en = u"Generic element"
)

translations.define("Item-plural",
    ca = u"Elements genèrics",
    es = u"Elementos genéricos",
    en = u"Generic elements"
)

translations.define("Item-none",
    ca = u"Cap",
    es = u"Ninguno",
    en = u"None"
)

translations.define("Item.administration",
    ca = u"Administració",
    es = u"Administración",
    en = u"Administration"
)

translations.define("Item.id",
    ca = u"ID",
    es = u"ID",
    en = u"ID"
)

translations.define("Item.qname",
    ca = u"Nom qualificat",
    es = u"Nombre cualificado",
    en = u"Qualified name"
)

translations.define("Item.author",
    ca = u"Autor",
    es = u"Autor",
    en = u"Author"
)

translations.define("Item.owner",
    ca = u"Propietari",
    es = u"Propietario",
    en = u"Owner"
)

translations.define("Item.changes",
    ca = u"Canvis",
    es = u"Cambios",
    en = u"Changes"
)

translations.define("Item.is_draft",
    ca = u"És esborrany",
    es = u"Es borrador",
    en = u"Is draft"
)

translations.define("Item.draft_source",
    ca = u"Original",
    es = u"Original",
    en = u"Master item"
)

translations.define("Item.drafts",
    ca = u"Esborranys",
    es = u"Borradores",
    en = u"Drafts"
)

translations.define("Item.creation_time",
    ca = u"Data de creació",
    es = u"Fecha de creación",
    en = u"Creation date"
)

translations.define("Item.last_update_time",
    ca = u"Última modificació",
    es = u"Última modificación",
    en = u"Last updated"
)

# Configuration
#------------------------------------------------------------------------------
translations.define("Configuration",
    ca = u"Configuració",
    es = u"Configuración",
    en = u"Configuration"
)

translations.define("Configuration-plural",
    ca = u"Configuració",
    es = u"Configuración",
    en = u"Configuration"
)

translations.define("Configuration.publication",
    ca = u"Publicació",
    es = u"Publicación",
    en = u"Publication"
)

translations.define("Configuration.publication.pages",
    ca = u"Pàgines especials",
    es = u"Páginas especiales",
    en = u"Special pages"
)

translations.define("Configuration.publication.maintenance",
    ca = u"Manteniment",
    es = u"Mantenimiento",
    en = u"Maintenance"
)

translations.define("Configuration.language",
    ca = u"Idioma",
    es = u"Idioma",
    en = u"Language"
)

translations.define("Configuration.media",
    ca = u"Multimèdia",
    es = u"Multimedia",
    en = u"Media"
)

translations.define("Configuration.media.images",
    ca = u"Imatges",
    es = u"Imagenes",
    en = u"Images"
)

translations.define("Configuration.media.video",
    ca = u"Vídeo",
    es = u"Video",
    en = u"Video"
)

translations.define("Configuration.rendering",
    ca = u"Processat d'imatges",
    es = u"Procesado de imágenes",
    en = u"Image processing"
)

translations.define("Configuration.services",
    ca = u"Serveis",
    es = u"Servicios",
    en = u"Services"
)

translations.define("Configuration.system",
    ca = u"Sistema",
    es = u"Sistema",
    en = u"System"
)

translations.define("Configuration.system.smtp",
    ca = u"Servidor SMTP",
    es = u"Servidor SMTP",
    en = u"SMTP server"
)

translations.define("Configuration.websites",
    ca = u"Pàgines web",
    es = u"Páginas web",
    en = u"Websites"
)

translations.define("Configuration.publication_schemes",
    ca = u"Esquemes de publicació",
    es = u"Esquemas de publicación",
    en = u"Publication schemes"
)

translations.define("Configuration.caching_policies",
    ca = u"Polítiques de cache",
    es = u"Políticas de cache",
    en = u"Caching policies"
)

translations.define("Configuration.login_page",
    ca = u"Pàgina d'autenticació",
    es = u"Página de autenticación",
    en = u"Authentication page"
)

translations.define("Configuration.generic_error_page",
    ca = u"Pàgina d'error genèric",
    es = u"Página de error genérico",
    en = u"Generic error page"
)

translations.define("Configuration.not_found_error_page",
    ca = u"Pàgina no trobada",
    es = u"Página no encontrada",
    en = u"Not found error page"
)

translations.define("Configuration.forbidden_error_page",
    ca = u"Pàgina d'error per accés restringit",
    es = u"Página de error por acceso restringido",
    en = u"Access forbidden page"
)

translations.define("Configuration.down_for_maintenance",
    ca = u"Lloc aturat per manteniment",
    es = u"Sitio parado por mantenimiento",
    en = u"Site down for maintenance"
)

translations.define("Configuration.maintenance_page",
    ca = u"Pàgina a mostrar durant el manteniment",
    es = u"Página a mostrar durante el mantenimiento",
    en = u"Service unavailable page"
)

translations.define("Configuration.maintenance_addresses",
    ca = u"Adreces IP que ignoren el mode de manteniment",
    es = u"Direcciones IP que ignoran el modo de mantenimiento",
    en = u"IP addresses that ignore maintenance mode"
)

translations.define("Configuration.languages",
    ca = u"Idiomes",
    es = u"Idiomas",
    en = u"Languages"
)

translations.define("Configuration.languages-explanation",
    ca = u"Llistat d'idiomes als que es pot traduïr el contingut. Cada "
         u"idioma s'indica mitjançant el seu codi ISO de dues lletres.",
    es = u"Listado de idiomas a los que se puede traducir el contenido. Cada "
         u"idioma se indica mediante su código ISO de dos letras.",
    en = u"Languages that content can be translated to. Each language is "
         u"specified using its two letter ISO code."
)

translations.define("Configuration.published_languages",
    ca = u"Idiomes publicats",
    es = u"Idiomas publicados",
    en = u"Published languages"
)

translations.define("Configuration.published_languages-explanation",
    ca = u"Limita els idiomes publicats al subconjunt indicat. Deixar en "
         u"blanc per permetre la publicació en qualsevol dels idiomes "
         u"disponibles.",
    es = u"Limita los idiomas publicados al subconjunto indicado. Dejar en "
         u"blanco para permitir la publicación en cualquiera de los idiomas "
         u"disponibles.",
    en = u"Limits publication to the indicated subset of languages. Leave "
         u"blank to allow publishing in any of the available languages."
)

translations.define("Configuration.default_language",
    ca = u"Idioma per defecte",
    es = u"Idioma por defecto",
    en = u"Default language"
)

translations.define("Configuration.heed_client_language",
    ca = u"Respectar les preferències d'idioma del navegador",
    es = u"Respetar las preferencias de idioma del navegador",
    en = u"Heed the language preferences from the browser"
)

translations.define("Configuration.backoffice_language",
    ca = u"Idioma per defecte de la interfície d'edició",
    es = u"Idioma por defecto de la interfaz de edición",
    en = u"Default language for the backoffice"
)    

translations.define("Configuration.renderers",
    ca = u"Pintadors",
    es = u"Pintadores",
    en = u"Renderers"
)

translations.define("Configuration.renderers-explanation",
    ca = u"Components encarregats de produïr una imatge representativa a "
         u"partir d'un tipus de contingut específic (imatges, PDFs, vídeos, "
         u"etc).",
    es = u"Componentes encargados de producir una imagen representativa a "
         u"partir de un tipo de contenido específico (imágenes, PDFs, "
         u"videos, etc).",
    en = u"Components tasked with producing images for different kinds of "
         u"content (ie. image files, PDF documents, videos, etc)."
)

translations.define("Configuration.image_factories",
    ca = u"Processadors d'imatges",
    es = u"Procesadores de imágenes",
    en = u"Image factories"
)

translations.define("Configuration.image_factories-explanation",
    ca = u"Les diferents variants de redimensionat i efectes que "
         u"s'apliquen a les imatges de la web.",
    es = u"Las distintas variaciones de redimensionado y efectos que "
         u"se aplican a las imágenes de la web.",
    en = u"The different resizing and transformation effects applied "
         u"to the site's images."
)

translations.define("Configuration.video_player_settings",
    ca = u"Opcions de reproductor de vídeo",
    es = u"Opciones de reproductor de video",
    en = u"Video player settings"
)

translations.define("Configuration.timezone",
    ca = u"Zona horària",
    es = u"Zona horaria",
    en = u"Timezone"
)

translations.define("Configuration.smtp_host",
    ca = u"Adreça del servidor SMTP",
    es = u"Dirección del servidor SMTP",
    en = u"SMTP host"
)

translations.define("Configuration.smtp_user",
    ca = u"Compte d'usuari del servidor SMTP",
    es = u"Cuenta de usuario del servidor SMTP",
    en = u"SMTP server user account"
)

translations.define("Configuration.smtp_password",
    ca = u"Contrasenya del servidor SMTP",
    es = u"Contraseña de usuario del servidor SMTP",
    en = u"SMTP server password"
)

translations.define("Configuration.triggers",
    ca = u"Disparadors",
    es = u"Disparadores",
    en = u"Triggers"
)

translations.define("Configuration.triggers-explanation",
    ca = u"Permet programar accions que s'activin quan es produeixin canvis "
         u"al contingut.",
    es = u"Permite programar acciones que se activen cuando se produzcan "
         u"cambios en el contenido",
    en = u"Program actions that will be activated when the site's content "
         u"changes."
)

# Website
#------------------------------------------------------------------------------
translations.define("Website",
    ca = u"Lloc web",
    es = u"Sitio web",
    en = u"Website"
)

translations.define("Website-plural",
    ca = u"Llocs web",
    es = u"Sitios web",
    en = u"Websites"
)

translations.define("Website.website",
    ca = u"Lloc web",
    es = u"Sitio web",
    en = u"Website"
)

translations.define("Website.contact",
    ca = u"Contacte",
    es = u"Contacto",
    en = u"Contact"
)

translations.define("Website.publication",
    ca = u"Publicació",
    es = u"Publicación",
    en = u"Publication"
)

translations.define("Website.publication.pages",
    ca = u"Pàgines especials",
    es = u"Páginas especiales",
    en = u"Special pages"
)

translations.define("Website.publication.maintenance",
    ca = u"Manteniment",
    es = u"Mantenimiento",
    en = u"Maintenance"
)

translations.define("Website.publication.https",
    ca = u"HTTPS",
    es = u"HTTPS",
    en = u"HTTPS"
)

translations.define("Website.language",
    ca = u"Idioma",
    es = u"Idioma",
    en = u"Language"
)

translations.define("Website.services",
    ca = u"Serveis",
    es = u"Servicios",
    en = u"Services"
)

translations.define("Website.site_name",
    ca = u"Nom del lloc",
    es = u"Nombre del sitio",
    en = u"Site name"
)

translations.define("Website.logo",
    ca = u"Logotip",
    es = u"Logotipo",
    en = u"Logo"
)

translations.define("Website.icon",
    ca = u"Icona",
    es = u"Icono",
    en = u"Icon"
)

translations.define("Website.keywords",
    ca = u"Paraules clau",
    es = u"Palabras clave",
    en = u"Keywords"
)

translations.define("Website.description",
    ca = u"Descripció",
    es = u"Descripción",
    en = u"Description"
)

translations.define("Website.hosts",
    ca = u"Dominis",
    es = u"Dominios",
    en = u"Hosts"
)

translations.define("Website.hosts-explanation",
    ca = u"La llista de dominis que han d'associar-se a aquesta web. "
         u"Poden utilitzar-se comodins (per exemple, *.foo.com).",
    es = u"La lista de dominios que deben asociarse a esta web. Pueden "
         u"utilizarse comodines (por ejemplo, *.foo.com).",
    en = u"The list of domains that can be associated to this website. Can "
         u"use wildcard expressions (such as *.foo.com)."
)

translations.define("Website.organization_name",
    ca = u"Nom de l'entitat",
    es = u"Nombre de la entidad",
    en = u"Entity name"
)

translations.define("Website.organization_url",
    ca = u"URL de l'entitat",
    es = u"URL de la entidad",
    en = u"Entity URL"
)

translations.define("Website.address",
    ca = u"Adreça",
    es = u"Dirección",
    en = u"Address"
)

translations.define("Website.town",
    ca = u"Localitat",
    es = u"Localidad",
    en = u"Town"
)

translations.define("Website.region",
    ca = u"Regió",
    es = u"Región",
    en = u"Region"
)

translations.define("Website.postal_code",
    ca = u"Codi postal",
    es = u"Código postal",
    en = u"Postal code"
)

translations.define("Website.country",
    ca = u"País",
    es = u"País",
    en = u"Country"
)

translations.define("Website.phone_number",
    ca = u"Telèfon",
    es = u"Teléfono",
    en = u"Phone number"
)

translations.define("Website.fax_number",
    ca = u"Fax",
    es = u"Fax",
    en = u"Fax"
)

translations.define("Website.email",
    ca = u"Correu electrònic",
    es = u"Correo electrónico",
    en = u"Email"
)

translations.define("Website.home",
    ca = u"Pàgina d'inici",
    es = u"Página de inicio",
    en = u"Home page"
)

translations.define("Website.login_page",
    ca = u"Pàgina d'autenticació",
    es = u"Página de autenticación",
    en = u"Authentication page"
)

translations.define("Website.generic_error_page",
    ca = u"Pàgina d'error genèric",
    es = u"Página de error genérico",
    en = u"Generic error page"
)

translations.define("Website.not_found_error_page",
    ca = u"Pàgina no trobada",
    es = u"Página no encontrada",
    en = u"Not found error page"
)

translations.define("Website.forbidden_error_page",
    ca = u"Pàgina d'error per accés restringit",
    es = u"Página de error por acceso restringido",
    en = u"Access forbidden page"
)

translations.define("Website.down_for_maintenance",
    ca = u"Lloc aturat per manteniment",
    es = u"Sitio parado por mantenimiento",
    en = u"Site down for maintenance"
)

translations.define("Website.maintenance_page",
    ca = u"Pàgina a mostrar durant el manteniment",
    es = u"Página a mostrar durante el mantenimiento",
    en = u"Service unavailable page"
)

translations.define("Website.https_policy",
    ca = u"Política de HTTPS",
    es = u"Política de HTTPS",
    en = u"HTTPS policy"
)

translations.define("Website.https_policy=always",
    ca = u"Habilitar a totes les pàgines",
    es = u"Habilitar en todas las páginas",
    en = u"Enable for all pages"
)

translations.define("Website.https_policy=never",
    ca = u"Deshabilitar a totes les pàgines",
    es = u"Deshabilitar en todas las páginas",
    en = u"Disable for all pages"
)

translations.define("Website.https_policy=per_page",
    ca = u"Decidir-ho a cada pàgina",
    es = u"Decidirlo en cada página",
    en = u"Decide on a per-page basis"
)

translations.define("Website.https_persistence",
    ca = u"Preservar HTTPS entre peticions",
    es = u"Preservar HTTPS entre peticiones",
    en = u"Persist HTTPS navigation across requests"
)

translations.define("Website.https_persistence-explanation",
    ca = u"Aquesta opció només tindrà efecte si la <em>Política "
         u"d'HTTPS</em> s'estableix a <em>Decidir a cada pàgina</em>.",
    es = u"Esta opción solo tendrá efecto si la <em>Política "
         u"de HTTPS</em> se establece a <em>Decidir en cada página</em>.",
    en = u"This option will only be taken into account if "
         u"<em>HTTPS policy</em> is set to <em>Decide on a per-page "
         u"basis</em>."
)

translations.define("Website.default_language",
    ca = u"Idioma per defecte",
    es = u"Idioma por defecto",
    en = u"Default language"
)

translations.define("Website.heed_client_language",
    ca = u"Respectar les preferències d'idioma del navegador",
    es = u"Respetar las preferencias de idioma del navegador",
    en = u"Heed the language preferences from the browser"
)

translations.define("Website.published_languages",
    ca = u"Idiomes publicats",
    es = u"Idiomas publicados",
    en = u"Published languages"
)

translations.define("Website.published_languages-explanation",
    ca = u"Limita els idiomes publicats al subconjunt indicat. Deixar en "
         u"blanc per permetre la publicació en qualsevol dels idiomes "
         u"disponibles.",
    es = u"Limita los idiomas publicados al subconjunto indicado. Dejar en "
         u"blanco para permitir la publicación en cualquiera de los idiomas "
         u"disponibles.",
    en = u"Limits publication to the indicated subset of languages. Leave "
         u"blank to allow publishing in any of the available languages."
)

translations.define("woost.views.LoginFormView.main",
    ca = u"""L'accés a aquesta secció del web està restringit. Per favor,
            introdueix les teves credencials d'usuari per continuar.""",
    es = u"""El acceso a esta sección del sitio está restringido. Por favor,
            introduce tus credenciales de usuario para continuar.""",
    en = u"""Access to this part of the website is restricted. Please, introduce
            your user credentials to proceed."""
)

translations.define("woost.views.LoginForm.forgot_password_link",
    ca = u"He oblidat la contrasenya",
    es = u"He olvidado la contraseña",
    en = u"I forgot my password"
)

translations.define("woost.views.LoginForm.submit_button",
    ca = u"Entrar",
    es = u"Entrar",
    en = u"Enter"
)

# PublicationScheme
#------------------------------------------------------------------------------
translations.define("PublicationScheme",
    ca = u"Esquema de publicació",
    es = u"Esquema de publicación",
    en = u"Publication scheme"
)

translations.define("PublicationScheme-plural",
    ca = u"Esquemes de publicació",
    es = u"Esquemas de publicación",
    en = u"Publication schemes"
)

# HierarchicalPublicationScheme
#------------------------------------------------------------------------------
translations.define("HierarchicalPublicationScheme",
    ca = u"Esquema de publicació jeràrquica",
    es = u"Esquema de publicación jerárquica",
    en = u"Hierarchical publication scheme"
)

translations.define("HierarchicalPublicationScheme-plural",
    ca = u"Esquemes de publicació jeràrquica",
    es = u"Esquemas de publicación jerárquica",
    en = u"Hierarchical publication schemes"
)

# IdPublicationScheme
#------------------------------------------------------------------------------
translations.define("IdPublicationScheme",
    ca = u"Esquema de publicació per ID",
    es = u"Esquema de publicación por ID",
    en = u"ID publication scheme"
)

translations.define("IdPublicationScheme-plural",
    ca = u"Esquemes de publicació per ID",
    es = u"Esquemas de publicación por ID",
    en = u"ID publication schemes"
)

# DescriptiveIdPublicationScheme
#------------------------------------------------------------------------------
translations.define("DescriptiveIdPublicationScheme",
    ca = u"Esquema de publicació per ID i descripció",
    es = u"Esquema de publicación por ID y descripción",
    en = u"ID plus description publication scheme"
)

translations.define("DescriptiveIdPublicationScheme-plural",
    ca = u"Esquemes de publicació per ID i descripció",
    es = u"Esquemas de publicación por ID y descripción",
    en = u"ID plus description publication schemes"
)

translations.define("DescriptiveIdPublicationScheme.id_separator",
    ca = u"Separador de l'ID",
    es = u"Separador de ID",
    en = u"ID separator"
)

translations.define("DescriptiveIdPublicationScheme.id_separator-explanation",
    ca = u"Fragment utilitzat per separar l'identificador de la descripció a "
         u"les URLs",
    es = u"Fragmento utilizado para separar el identificador de la "
         u"descripción en las URLs",
    en = u"Token used to separate identifiers from descriptive text in URLs"
)

translations.define("DescriptiveIdPublicationScheme.word_separator",
    ca = u"Separador de paraules",
    es = u"Separador de palabras",
    en = u"Word separator"
)

translations.define("DescriptiveIdPublicationScheme.word_separator-explanation",
    ca = u"Fragment utilitzat per separar les paraules del títol a les URLs",
    es = u"Fragmento utilizado para separar las palabras del título en las "
         u"URLs",
    en = u"A token used as a word separator for titles in URLs"
)

translations.define("DescriptiveIdPublicationScheme.id_regexp",
    ca = u"Expressió d'extracció de l'ID",
    es = u"Expresión de extracción del ID",
    en = u"ID extraction expression"
)

translations.define("DescriptiveIdPublicationScheme.id_regexp-explanation",
    ca = u"L'expressió regular utilitzada per obtenir l'identificador d'un "
         u"element a partir de la seva URL. Ha de contenir un grup anomenat "
         u"<em>id</em>.",
    es = u"La expresión regular utilizada para obtener el identificador de un "
         u"elemento a partir de su URL. Debe contener un grupo llamado "
         u"<em>id</em>.",
    en = u"The regular expression used to extract the identifier of a "
         u"publishable item from its URL. Must define an <em>id</em> named "
         u"group."
)

translations.define("DescriptiveIdPublicationScheme.title_splitter_regexp",
    ca = u"Expressió de divisió del títol",
    es = u"Expresión de separación del título",
    en = u"Title splitter expression"
)

translations.define(
    "DescriptiveIdPublicationScheme.title_splitter_regexp-explanation",
    ca = u"L'expressió regular utilitzada per desestimar les parts "
         u"irrellevants d'un títol",
    es = u"La expresión regular utilizada para desestimar las partes "
         u"irrelevantes de un título",
    en = u"The regular expression used to discard irrelevant parts from a "
         u"title"
)

translations.define("DescriptiveIdPublicationScheme.format",
    ca = u"Format de les URLs",
    es = u"Formato de las URLs",
    en = u"URL format"
)

translations.define("DescriptiveIdPublicationScheme.format-explanation",
    ca = u"Una cadena de formatat de text python. Rep <em>title</em>, "
         u"<em>id</em> i <em>separator</em> com a paràmetres.",
    es = u"Una cadena de formatado de texto python. Recibe <em>title</em>, "
         u"<em>id</em> y <em>separator</em> como parámetros.",
    en = u"A python text formatting string that takes <em>title</em>, "
         u"<em>id</em> and <em>separator</em> parameters."
)

translations.define("DescriptiveIdPublicationScheme.include_file_extensions",
    ca = u"Incloure extensions de fitxer",
    es = u"Incluir extensiones de fichero",
    en = u"Include file extensions"
)

# CachingPolicy
#------------------------------------------------------------------------------
translations.define("CachingPolicy",
    ca = u"Política de cache",
    es = u"Política de cache",
    en = u"Caching policy"
)

translations.define("CachingPolicy-plural",
    ca = u"Polítiques de cache",
    es = u"Políticas de cache",
    en = u"Caching policies"
)

translations.define("CachingPolicy.description",
    ca = u"Descripció",
    es = u"Descripción",
    en = u"Description"
)

translations.define("CachingPolicy.important",
    ca = u"Important",
    es = u"Importante",
    en = u"Important"
)

translations.define("CachingPolicy.important-explanation",
    ca = u"Indica que la regla s'aplica abans que la resta.",
    es = u"Indica que la regla se aplica antes que el resto.",
    en = u"Indicates that this rule should be applied before the rest."
)

translations.define("CachingPolicy.cache_enabled",
    ca = u"Cache habilitat",
    es = u"Cache habilitado",
    en = u"Cache enabled"
)

translations.define("CachingPolicy.cache_enabled-explanation",
    ca = u"Si s'habilita el cache, els elements sol·licitats pels usuaris "
         u"només són reprocessats quan han estat modificats. Això millora "
         u"notablement el rendiment, però per contra no garanteix que el "
         u"contingut que es mostra estigui actualitzat a la última "
         u"versió.",
    es = u"Si se habilita el cache, los elementos solicitados por los "
         u"usuarios solo son procesados si han sido modificados. Esto "
         u"mejora notablemente el rendimiento, pero por contra no "
         u"garantiza que el contenido que se muestra a los usuarios esté "
         u"actualizado a la última versión.",
    en = u"Enabling caching for this item will cause the application to "
         u"only process items if they have been modified. This can "
         u"greatly increase performance, at the expense of being unable "
         u"to guarantee that users are served the latest version of the "
         u"content."
)

translations.define("CachingPolicy.server_side_cache",
    ca = u"Cache de servidor habilitat",
    es = u"Cache de servidor habilitado",
    en = u"Server side cache enabled"
)

translations.define("CachingPolicy.server_side_cache-explanation",
    ca = u"Habilitar per mantenir el contingut publicable de l'element "
         u"en memòria. Això accelera el temps de resposta, però "
         u"augmenta els recursos consumits per l'aplicació.",
    es = u"Habilitar para mantener el contenido publicable del elemento "
         u"en memoria. Esto acelera los tiempos de respuesta, pero "
         u"aumenta los recursos consumidos por la aplicación.",
    en = u"Enable to maintain the item's rendered content in memory. This "
         u"minimizes response times, but increases the amount of memory "
         u"consumed by the application."
)

translations.define("CachingPolicy.expiration_expression",
    ca = u"Expiració del cache",
    es = u"Expiración del cache",
    en = u"Cache expiration"
)

translations.define("CachingPolicy.expiration_expression-explanation",
    ca = u"""
        <p>
            Fragment de codi Python que determina la duració de les entrades
            de cache generades per aquesta política.
        </p>
        <details>
            <summary>Detalls</summary>
            <p>
                Si el camp es deixa en blanc es desactiva l'expiració de les
                entrades, que es mantindran actives fins que s'invalidin per
                altres vies (com ara una actualització de l'<em>última
                modificació</em> de l'element publicable).
            </p>
            <p>
                L'expiració s'estableix amb una variable <em>expiration</em>, que pot
                expressar-se utilitzant qualsevol dels tipus següents:
            </p>
            <dl>
                <dt>int</dt>
                <dd>Vigència de l'entrada, en minuts.</dd>
                <dt><a href="http://docs.python.org/2/library/datetime.html#timedelta-objects">timedelta</a></dt>
                <dd>Vigència de l'entrada, expressada en diferents unitats (minuts,
                hores, dies, etc).</dd>
                <dt><a href="http://docs.python.org/2/library/datetime.html#datetime-objects">datetime</a></dt>
                <dd>Data exacta en que l'entrada es considerarà expirada.</dd>
                <dt>None</dt>
                <dd>Duració sense determinar, l'entrada no expirarà
                automàticament.</dd>
            </dl>
            <p>
                L'expressió rep una variable <em>publishable</em> (la
                referència a l'element publicable al que s'aplica la política
                de cache), així com referències a les classes
                <em>datetime</em> i <em>timedelta</em> (com a conveniència,
                per no haver-les d'importar explícitament).
            </p>
        </details>
        """,
    es = u"""
        <p>
            Fragmento de código Python que determina la duración de las
            entradas de cache generadas por esta política.
        </p>
        <details>
            <summary>Detalles</summary>
            <p>
                Si el campo se deja en blanco se desactiva la expiración de
                las entradas, que se mantendrán activas hasta que se invaliden
                por otras vías (como una actualización de la <em>última
                modificación</em> del elemento publicable).
            </p>
            <p>
                La expiración se establece con una variable
                <em>expiration</em>, que puede expresarse mediante
                cualquiera de los siguientes tipos:
            </p>
            <dl>
                <dt>int</dt>
                <dd>Vigencia de la entrada, en minutos.</dd>
                <dt><a href="http://docs.python.org/2/library/datetime.html#timedelta-objects">timedelta</a></dt>
                <dd>Vigencia de la entrada, expresada en distintas unidades
                (minutos, horas, días, etc).</dd>
                <dt><a href="http://docs.python.org/2/library/datetime.html#datetime-objects">datetime</a></dt>
                <dd>Fecha exacta en que la entrada se considerará expirada.</dd>
                <dt>None</dt>
                <dd>Duración sin determinar, la entrada no expirará
                automáticamente.</dd>
            </dl>
            <p>
                La expresión recibe una variable <em>publishable</em> (la
                referencia al elemento publicable al que se aplica la política
                de cache), así como referencias a las clases <em>datetime</em>
                y <em>timedelta</em> (como conveniencia, para no tener que
                importar estos tipos explícitamente).
            </p>
        </details>
        """,
    en = u"""
        <p>
            A Python code block that determines the duration of the cache
            entries generated by this caching policy. 
        </p>
        <details>
            <summary>Details</summary>
            <p>
                If the field is left blank, cache entries will not expire, and
                they will have to rely on other means in order to be
                invalidated (such as a change in the <em>last update</em> of
                the publishable element).
            </p>
            <p>
                Entry duration is expressed using an <em>expiration</em>
                variable, using any of the following types:
            </p>
            <dl>
                <dt>int</dt>
                <dd>Expresses entry duration in minutes.</dd>
                <dt><a href="http://docs.python.org/2/library/datetime.html#timedelta-objects">timedelta</a></dt>
                <dd>Expresses entry duration using a variety of units (minutes,
                hours, days, etc).</dd>
                <dt><a href="http://docs.python.org/2/library/datetime.html#datetime-objects">datetime</a></dt>
                <dd>Exact date when the entry will expire.</dd>
                <dt>None</dt>
                <dd>Undefined duration, the entry won't expire on its own.</dd>
            </dl>
            <p>
                The expression receives a <em>publishable</em> variable (the
                publishable element that the cached content is being generated
                for), as well as references to the <em>datetime</em> and
                <em>timedelta</em> standard types (as a convenience, to avoid
                having to import them explicitly).
            </p>
        </details>
        """
)

translations.define("CachingPolicy.condition",
    ca = u"Condició",
    es = u"Condición",
    en = u"Condition"
)

translations.define("CachingPolicy.condition-explanation",
    ca = u"Una expressió que especifica les circumstàncies necessàries "
         u"perquè s'apliqui aquesta política de cache.",
    es = u"Una expresión que especifica las circunstancias necesarias "
         u"para que se aplique esta política de cache.",
    en = u"An expression describing the necessary conditions for this "
         u"caching policy to be applied."
)

translations.define("CachingPolicy.cache_key_expression",
    ca = u"Clau de cache",
    es = u"Clave de cache",
    en = u"Cache key"
)

translations.define("CachingPolicy.cache_key_expression-explanation",
    ca = u"Una expressió que determina l'entrada al cache que correspon a la "
         u"petició en curs. Deixar en blanc per utilitzar l'expressió per "
         u"defecte.",
    es = u"Una expresión que determina la entrada en cache que le "
         u"corresponde a la petición en curso. Dejar en blanco para usar la "
         u"expresión por defecto.",
    en = u"An expression that designates which cache entry should be used by "
         u"the active request. Leave blank to use the default expression."
)

translations.define("CachingPolicy.last_update_expression",
    ca = u"Última modificació",
    es = u"Última modificación",
    en = u"Last update"
)

translations.define("CachingPolicy.last_update_expression-explanation",
    ca = u"Una expressió que determina la data de la última modificació del "
         u"document i el seu contingut relacionat. El contingut en cache "
         u"anterior a aquesta data serà descartat automàticament.",
    es = u"Una expresión que determina la fecha de la última modificación del "
         u"documento y su contenido relacionado. El contenido en cache "
         u"anterior a esta fecha será descartado automáticamente.",
    en = u"An expression indicating the date of the latest revision of the "
         u"document's content. Cached content older than this will be "
         u"automatically discarded."
)

# Publishable
#------------------------------------------------------------------------------
translations.define("Publishable",
    ca = u"Element publicable",
    es = u"Elemento publicable",
    en = u"Publishable element"
)

translations.define("Publishable-plural",
    ca = u"Elements publicables",
    es = u"Elementos publicables",
    en = u"Publishable elements"
)

translations.define("Publishable.meta",
    ca = u"Metadades",
    es = u"Metadatos",
    en = u"Metadata"
)

translations.define("Publishable.presentation",
    ca = u"Presentació",
    es = u"Presentación",
    en = u"Presentation"
)

translations.define("Publishable.presentation.behavior",
    ca = u"Comportament",
    es = u"Comportamiento",
    en = u"Behavior"
)

translations.define("Publishable.presentation.resources",
    ca = u"Recursos",
    es = u"Recursos",
    en = u"Resources"
)

translations.define("Publishable.presentation.format",
    ca = u"Format",
    es = u"Formato",
    en = u"Format"
)

translations.define("Publishable.navigation",
    ca = u"Navegació",
    es = u"Navegación",
    en = u"Navigation"
)

translations.define("Publishable.publication",
    ca = u"Publicació",
    es = u"Publicación",
    en = u"Publication"
)

translations.define("Publishable.resource_type",
    ca = u"Tipus de recurs",
    es = u"Tipo de recurso",
    en = u"Resource type"
)

translations.define("Publishable.encoding",
    ca = u"Codificació de text",
    es = u"Codificación del texto",
    en = u"Text encoding"
)

translations.define("woost.models.Publishable.resource_type text",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

translations.define("woost.models.Publishable.resource_type image",
    ca = u"Imatge",
    es = u"Imagen",
    en = u"Image"
)

translations.define("woost.models.Publishable.resource_type audio",
    ca = u"Audio",
    es = u"Audio",
    en = u"Audio"
)

translations.define("woost.models.Publishable.resource_type video",
    ca = u"Video",
    es = u"Video",
    en = u"Video"
)

translations.define("woost.models.Publishable.resource_type package",
    ca = u"Paquet",
    es = u"Paquete",
    en = u"Package"
)

translations.define("woost.models.Publishable.resource_type document",
    ca = u"Document",
    es = u"Documento",
    en = u"Document"
)

translations.define("woost.models.Publishable.resource_type html_resource",
    ca = u"Recurs HTML",
    es = u"Recurso HTML",
    en = u"HTML resource"
)

translations.define("woost.models.Publishable.resource_type other",
    ca = u"Altre",
    es = u"Otro",
    en = u"Other"
)

translations.define("Publishable.inherit_resources",
    ca = u"Hereda els recursos",
    es = u"Hereda los recursos",
    en = u"Inherit resources"
)

translations.define("Publishable.mime_type",
    ca = u"Tipus MIME",
    es = u"Tipo MIME",
    en = u"MIME type"
)

translations.define("Publishable.per_language_publication",
    ca = u"Publicació per idiomes",
    es = u"Publicación por idiomas",
    en = u"Per language publication"
)

translations.define("Publishable.enabled",
    ca = u"Actiu",
    es = u"Activo",
    en = u"Enabled"
)

translations.define("Publishable.translation_enabled",
    ca = u"Traducció activa",
    es = u"Traducción activa",
    en = u"Translation is enabled"
)

translations.define("Publishable.websites",
    ca = u"Webs on es publica",
    es = u"Webs donde se publica",
    en = u"Websites where it is published"
)

translations.define("Publishable.websites-explanation",
    ca = u"Webs des de les que es podrà veure i accedir a l'element. Deixar "
         u"en blanc per permetre que l'element aparegui a totes les webs.",
    es = u"Webs des de las que se podrá ver y acceder al elemento. Dejar en "
         u"blanco para permitir que el elemento aparezca en todas las webs.",
    en = u"Websites where the element will be published. Leave blank to share "
         u"this element across all websites."
)

translations.define("Publishable.hidden",
    ca = u"Ocult",
    es = u"Oculto",
    en = u"Hidden"
)

translations.define("Publishable.start_date",
    ca = u"Data de publicació",
    es = u"Fecha de publicación",
    en = u"Publication date"
)

translations.define("Publishable.end_date",
    ca = u"Data de caducitat",
    es = u"Fecha de caducidad",
    en = u"Expiration date"
)

translations.define("Publishable.requires_https",
    ca = u"Requereix HTTPS",
    es = u"Requiere HTTPS",
    en = u"Requires HTTPS"
)

translations.define("Publishable.requires_https-explanation",
    ca = u"Aquesta opció només tindrà efecte si la <em>Política "
         u"d'HTTPS</em> del lloc web s'estableix a <em>Decidir a cada "
         u"pàgina</em>.",
    es = u"Esta opción solo tendrá efecto si la <em>Política "
         u"de HTTPS</em> del sitio web se establece a <em>Decidir en cada "
         u"página</em>.",
    en = u"This option will only be taken into account if the site's "
         u"<em>HTTPS policy</em> is set to <em>Decide on a per-page "
         u"basis</em>."
)

translations.define("Publishable.controller",
    ca = u"Controlador",
    es = u"Controlador",
    en = u"Controller"
)

translations.define("Publishable.parent",
    ca = u"Pare",
    es = u"Padre",
    en = u"Parent"
)

translations.define("Publishable.path",
    ca = u"Ruta",
    es = u"Ruta",
    en = u"Path"
)

translations.define("Publishable.full_path",
    ca = u"Ruta completa",
    es = u"Ruta completa",
    en = u"Full path"
)

translations.define("Publishable.caching_policies",
    ca = u"Polítiques de cache",
    es = u"Políticas de cache",
    en = u"Caching policies"
)

translations.define("Publishable.caching_policy-explanation",
    ca = u"Permet establir una política de cache específica per a "
         u"l'element. Si es deixa en blanc s'utilitzarà la política general "
         u"del lloc web.",
    es = u"Permite establecer una política de cache específica para el "
         u"elemento. Si se deja en blanco se utilizará la política general "
         u"del sitio web.",
    en = u"Sets a specific caching policy for this item. Leave blank to fall "
         u"back to the site wide caching policy." 
)

translations.define("Publishable.login_page",
    ca = u"Pàgina d'autorització",
    es = u"Página de autorización",
    en = u"Authorization page"
)

translations.define("Publishable.login_page-explanation",
    ca = u"Permet dotar l'element i les seves pàgines filles d'una pàgina "
         u"d'autenticació pròpia. Deixar buit per utilitzar el mateix "
         u"formulari que la resta del lloc web.",
    es = u"Permite dotar al elemento y a sus páginas hijas de una página "
         u"de autenticación propia. Dejar vacío para utilizar el mismo "
         u"formulario que el resto del sitio.",
    en = u"If set, indicates an alternative authentication page to use when "
         u"restricting access to this element or its descending pages. Leave "
         u"blank to use the same authentication form as the rest of the site."
)

# Page
#------------------------------------------------------------------------------
translations.define("Document",
    ca = u"Document",
    es = u"Documento",
    en = u"Document"
)

translations.define("Document-plural",
    ca = u"Documents",
    es = u"Documentos",
    en = u"Documents"
)

translations.define("Document.content",
    ca = u"Contingut",
    es = u"Contenido",
    en = u"Content"
)

translations.define("Document.meta.robots",
    ca = u"Robots",
    es = u"Robots",
    en = u"Robots"
)

translations.define("Document.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("Document.inner_title",
    ca = u"Títol interior",
    es = u"Título interior",
    en = u"Inner title"
)

translations.define("Document.description",
    ca = u"Descripció",
    es = u"Descripción",
    en = u"Description"
)

translations.define("Document.keywords",
    ca = u"Paraules clau",
    es = u"Palabras clave",
    en = u"Keywords"
)

translations.define("Document.template",
    ca = u"Plantilla",
    es = u"Plantilla",
    en = u"Template"
)

translations.define("Document.attachments",
    ca = u"Adjunts",
    es = u"Adjuntos",
    en = u"Attachments"
)

translations.define("Document.page_resources",
    ca = u"Recursos de pàgina",
    es = u"Recursos de pàgina",
    en = u"Page resources"
)

translations.define("Document.branch_resources",
    ca = u"Recursos de branca",
    es = u"Recursos de rama",
    en = u"Branch resources"
)

translations.define("Document.children",
    ca = u"Pàgines filles",
    es = u"Páginas hijas",
    en = u"Child pages"
)

translations.define("Document.redirection_mode",
    ca = u"Modalitat de redirecció",
    es = u"Modalidad de redirección",
    en = u"Redirection mode"
)

translations.define("Document.redirection_mode=first_child",
    ca = u"Redirigir al primer fill accessible",
    es = u"Redirigir al primer hijo accesible",
    en = u"Redirect to the first accessible child"
)

translations.define("Document.redirection_mode=custom_target",
    ca = u"Redirigir a un element concret",
    es = u"Redirigir a un elemento concreto",
    en = u"Redirect to a custom target"
)

translations.define("Document.redirection_target",
    ca = u"Destí de la redirecció",
    es = u"Destino de la redirección",
    en = u"Redirection target"
)

translations.define("Document.robots_should_index",
    ca = u"Contingut indexable",
    es = u"Contenido indexable",
    en = u"Indexable content"
)

translations.define("Document.robots_should_follow",
    ca = u"Seguir els enllaços",
    es = u"Seguir los enlaces",
    en = u"Follow links"
)

# Redirection
#------------------------------------------------------------------------------
translations.define("Redirection",
    ca = u"Redirecció",
    es = u"Redirección",
    en = u"Redirection"
)

translations.define("Redirection-plural",
    ca = u"Redireccions",
    es = u"Redirecciones",
    en = u"Redirections"
)

translations.define("Redirection.uri",
    ca = u"URL",
    es = u"URL",
    en = u"URL"
)

# StandardPage
#------------------------------------------------------------------------------
translations.define("StandardPage",
    ca = u"Pàgina estàndard",
    es = u"Página estándar",
    en = u"Standard page"
)

translations.define("StandardPage-plural",
    ca = u"Pàgines estàndard",
    es = u"Páginas estándar",
    en = u"Standard pages"
)

translations.define("StandardPage-none",
    es = u"Ninguna"
)

translations.define("StandardPage.body",
    ca = u"Cos",
    es = u"Cuerpo",
    en = u"Body"
)

# User
#------------------------------------------------------------------------------
translations.define("User",
    ca = u"Usuari",
    es = u"Usuario",
    en = u"User"
)

translations.define("User-plural",
    ca = u"Usuaris",
    es = u"Usuarios",
    en = u"Users"
)

translations.define("User.email",
    ca = u"Correu electrònic",
    es = u"Correo electrónico",
    en = u"E-mail address",
    pt = u"Email"
)

translations.define("User.password",
    ca = u"Contrasenya",
    es = u"Contraseña",
    en = u"Password",
    pt = u"Palavra-passe",
)

translations.define("User.prefered_language",
    ca = u"Idioma del gestor de continguts",
    es = u"Idioma del gestor de contenidos",
    en = u"Back office language"
)

translations.define("User.authored_items",
    ca = u"Contingut creat per l'usuari",
    es = u"Contingut creado por el usuario",
    en = u"Content created by the user"
)

translations.define("User.owned_items",
    ca = u"Contingut propietat de l'usuari",
    es = u"Contingut propiedad del usuario",
    en = u"Content owned by the user"
)

translations.define("User.roles",
    ca = u"Rols",
    es = u"Roles",
    en = u"Roles"
)

translations.define("User.enabled",
    ca = u"Activat",
    es = u"Activado",
    en = u"Enabled"
)

# Permission
#------------------------------------------------------------------------------
translations.define("Permission",
    ca = u"Permís",
    es = u"Permiso",
    en = u"Permission"
)

translations.define("Permission-plural",
    ca = u"Permisos",
    es = u"Permisos",
    en = u"Permissions"
)

translations.define("Permission.role",
    ca = u"Rol",
    es = u"Rol",
    en = u"Role"
)

translations.define("Permission.authorized",
    ca = u"Autoritzat",
    es = u"Autorizado",
    en = u"Authorized"
)

translations.define("Permission.authorized-explanation",
    ca = u"Si es desmarca, el permís passa a actuar com una prohibició",
    es = u"Si se desmarca, el permiso pasa a actuar como una prohibición",
    en = u"If unchecked, the permission is treated as a prohibition"
)

def permission_translation_factory(language, predicate):

    def translate_permission(instance, **kwargs):
        return translations(
            "woost.models.permission",
            language,
            authorized = instance.authorized,
            predicate = predicate(instance, **kwargs)
        )

    return translate_permission

def content_permission_translation_factory(language, predicate):
    
    def predicate_factory(instance, **kwargs):
        subject = translations(
            instance.select_items(),
            language,
            **kwargs
        )

        if hasattr(predicate, "__call__"):
            return predicate(instance, subject, **kwargs)
        else:
            return predicate % subject

    return permission_translation_factory(
        language,
        predicate_factory
    )

MEMBER_PERMISSION_ABBR_THRESHOLD = 4

def member_permission_translation_factory(
    language,
    predicate,
    enum,
    abbr,
    any_predicate
):
    def predicate_factory(instance, **kwargs):
        
        members = list(instance.iter_members())

        if not members:
            target = any_predicate

        elif len(members) >= MEMBER_PERMISSION_ABBR_THRESHOLD:
            counter = OrderedDict()

            for member in members:
                counter[member.schema] = counter.get(member.schema, 0) + 1

            target = u", ".join(
                abbr(count, content_type)
                for content_type, count in counter.iteritems()
            )
        else:
            subject = u", ".join(
                translations(member, language, qualified = True)
                for member in members
            )

            if hasattr(enum, "__call__"):
                target = enum(instance, subject, **kwargs)
            else:
                target = enum % subject

        return predicate % target

    return permission_translation_factory(
        language,
        predicate_factory
    )

def language_permission_translation_factory(language, predicate, any_predicate):

    def predicate_factory(instance, **kwargs):
        
        if not instance.matching_languages:
            return any_predicate

        subject = u", ".join(
            translations(perm_lang, language)
            for perm_lang in instance.matching_languages
        )

        if hasattr(predicate, "__call__"):
            return predicate(instance, subject, **kwargs)
        else:
            return predicate % subject

    return permission_translation_factory(
        language,
        predicate_factory
    )

translations.define("woost.models.permission",
    ca = lambda authorized, predicate: 
        u"Permís per " + predicate
        if authorized
        else u"Prohibició " + ca_possessive(predicate),
    es = lambda authorized, predicate:
        (u"Permiso para " if authorized else u"Prohibición de ") + predicate,
    en = lambda authorized, predicate:
        (u"Permission to " if authorized else u"Prohibition to ") + predicate,
)

translations.define(
    "woost.models.permission.ReadPermission-instance",
    ca = content_permission_translation_factory("ca", u"llegir %s"),
    es = content_permission_translation_factory("es", u"leer %s"),
    en = content_permission_translation_factory("en", u"read %s")
)

translations.define(
    "woost.models.permission.CreatePermission-instance",
    ca = content_permission_translation_factory("ca", u"crear %s"),
    es = content_permission_translation_factory("es", u"crear %s"),
    en = content_permission_translation_factory("en", u"create %s")
)

translations.define(
    "woost.models.permission.ModifyPermission-instance",
    ca = content_permission_translation_factory("ca", u"modificar %s"),
    es = content_permission_translation_factory("es", u"modificar %s"),
    en = content_permission_translation_factory("en", u"modify %s")
)

translations.define(
    "woost.models.permission.DeletePermission-instance",
    ca = content_permission_translation_factory("ca", u"eliminar %s"),
    es = content_permission_translation_factory("es", u"eliminar %s"),
    en = content_permission_translation_factory("en", u"delete %s")
)

translations.define(
    "woost.models.permission.ConfirmDraftPermission-instance",
    ca = content_permission_translation_factory(
        "ca",
        lambda permission, subject, **kwargs:
            u"confirmar esborranys " + ca_possessive(subject)
    ),
    es = content_permission_translation_factory(
        "es",
        u"confirmar borradores de %s"
    ),
    en = content_permission_translation_factory("en", u"confirm drafts of %s")
)

translations.define(
    "woost.models.permission.RenderPermission-instance",
    ca = content_permission_translation_factory(
        "ca",
        lambda permission, subject, **kwargs:
            u"generar imatges " + ca_possessive(subject)
    ),
    es = content_permission_translation_factory(
        "es",
        u"generar imágenes de %s"
    ),
    en = content_permission_translation_factory("en", u"render %s")
)

translations.define(
    "woost.models.permission.ReadMemberPermission-instance",
    ca = member_permission_translation_factory("ca",
        u"llegir %s",
        lambda instance, subject, **kwargs:
            plural2(
                len(instance.matching_members),
                u"el membre %s",
                u"els membres %s"
            ) % subject,
        lambda count, content_type, **kwargs:
            plural2(count, u"1 membre ", u"%d membres " % count)
            + ca_possessive(translations(content_type.name)),
        u"qualsevol membre"
    ),
    es = member_permission_translation_factory("es",
        u"leer %s",
        lambda instance, subject, **kwargs:
            plural2(
                len(instance.matching_members),
                u"el miembro %s",
                u"los miembros %s"
            ) % subject,
        lambda count, content_type, **kwargs:
            plural2(count, u"1 miembro", u"%d miembros" % count)
            + u" de " + (translations(content_type.name)),
        u"cualquier miembro"
    ),
    en = member_permission_translation_factory("en",
        u"read %s",
        lambda instance, subject, **kwargs:
            plural2(
                len(instance.matching_members),
                u"the %s member",
                u"the %s members"
            ) % subject,
        lambda count, content_type, **kwargs:
            plural2(count, u"1 member", u"%d members" % count)
            + u" of " + (translations(content_type.name)),
        u"any member"
    )
)

translations.define(
    "woost.models.permission.ModifyMemberPermission-instance",
    ca = member_permission_translation_factory("ca",
        u"modificar %s",
        lambda instance, subject, **kwargs:
            plural2(
                len(instance.matching_members),
                u"el membre %s", 
                u"els membres %s"
            ) % subject,
        lambda count, content_type, **kwargs:
            plural2(count, u"1 membre ", u"%d membres " % count)
            + ca_possessive(translations(content_type.name)),
        u"qualsevol membre"
    ),
    es = member_permission_translation_factory("es",
        u"modificar %s",
        lambda instance, subject, **kwargs:
            plural2(
                len(instance.matching_members),
                u"el miembro %s", 
                u"los miembros %s"
            ) % subject,
        lambda count, content_type, **kwargs:
            plural2(count, u"1 miembro", u"%d miembros" % count)
            + u" de " + (translations(content_type.name)),
        u"cualquier miembro"
    ),
    en = member_permission_translation_factory("en",
        u"modify %s",
        lambda instance, subject, **kwargs:
            plural2(
                len(instance.matching_members),
                u"the %s member", 
                u"the %s members"
            ) % subject,
        lambda count, content_type, **kwargs:
            plural2(count, u"1 member", u"%d members" % count)
            + u" of " + (translations(content_type.name)),
        u"any member"
    )
)

translations.define(
    "woost.models.permission.ReadTranslationPermission-instance",
    ca = language_permission_translation_factory("ca",
        u"llegir traduccions: %s", u"llegir qualsevol traducció"
    ),
    es = language_permission_translation_factory("es",
        u"leer traducciones: %s", u"leer cualquier traducción"
    ),
    en = language_permission_translation_factory("en",
        u"read translations: %s", u"read any translation"
    )
)

translations.define(
    "woost.models.permission.CreateTranslationPermission-instance",
    ca = language_permission_translation_factory("ca",
        u"crear traduccions: %s", u"crear qualsevol traducció"
    ),
    es = language_permission_translation_factory("es",
        u"crear traducciones: %s", u"crear cualquier traducción"
    ),
    en = language_permission_translation_factory("en",
        u"create translations: %s", u"create any translation"
    )
)

translations.define(
    "woost.models.permission.ModifyTranslationPermission-instance",
    ca = language_permission_translation_factory("ca",
        u"modificar traduccions: %s", u"modificar qualsevol traducció"
    ),
    es = language_permission_translation_factory("es",
        u"modificar traducciones: %s", u"modificar cualquier traducción"
    ),
    en = language_permission_translation_factory("en",
        u"modify translations: %s", u"modify any translation"
    )
)

translations.define(
    "woost.models.permission.DeleteTranslationPermission-instance",
    ca = language_permission_translation_factory("ca",
        u"eliminar traduccions: %s", u"eliminar qualsevol traducció"
    ),
    es = language_permission_translation_factory("es",
        u"eliminar traducciones: %s", u"eliminar cualquier traducción"
    ),
    en = language_permission_translation_factory("en",
        u"delete translations: %s", u"delete any translation"
    )
)

# ContentPermission
#------------------------------------------------------------------------------
translations.define("ContentPermission",
    ca = u"Permís de contingut",
    es = u"Permiso de contenido",
    en = u"Content permission"
)

translations.define("ContentPermission-plural",
    ca = u"Permisos de contingut",
    es = u"Permisos de contenido",
    en = u"Content permissions"
)

translations.define("ContentPermission.matching_items",
    ca = u"Elements inclosos",
    es = u"Elementos incluidos",
    en = u"Included items"
)

# ReadPermission
#------------------------------------------------------------------------------
translations.define("ReadPermission",
    ca = u"Permís de lectura",
    es = u"Permiso de lectura",
    en = u"Read content permission"
)

translations.define("ReadPermission-plural",
    ca = u"Permisos de lectura",
    es = u"Permisos de lectura",
    en = u"Read content permissions"
)

# CreatePermission
#------------------------------------------------------------------------------
translations.define("CreatePermission",
    ca = u"Permís de creació",
    es = u"Permiso de creación",
    en = u"Create content permission"
)

translations.define("CreatePermission-plural",
    ca = u"Permisos de creació",
    es = u"Permisos de creación",
    en = u"Create content permissions"
)

# ModifyPermission
#------------------------------------------------------------------------------
translations.define("ModifyPermission",
    ca = u"Permís de modificació",
    es = u"Permiso de modificación",
    en = u"Modify content permission"
)

translations.define("ModifyPermission-plural",
    ca = u"Permisos de modificació",
    es = u"Permisos de modificación",
    en = u"Modify content permissions"
)

# DeletePermission
#------------------------------------------------------------------------------
translations.define("DeletePermission",
    ca = u"Permís d'eliminació",
    es = u"Permiso de eliminación",
    en = u"Delete content permission"
)

translations.define("DeletePermission-plural",
    ca = u"Permisos d'eliminació",
    es = u"Permisos de eliminación",
    en = u"Delete content permissions"
)

# ConfirmDraftPermission
#------------------------------------------------------------------------------
translations.define("ConfirmDraftPermission",
    ca = u"Permís de confirmació d'esborranys",
    es = u"Permiso de confirmación de borradores",
    en = u"Confirm draft permission"
)

translations.define("ConfirmDraftPermission-plural",
    ca = u"Permisos de confirmació d'esborranys",
    es = u"Permisos de confirmación de borradores",
    en = u"Confirm draft permissions"
)

# RenderPermission
#------------------------------------------------------------------------------
translations.define("RenderPermission",
    ca = u"Permís de visualització d'imatges",
    es = u"Permiso de visualización de imágenes",
    en = u"Render permission"
)

translations.define("RenderPermission-plural",
    ca = u"Permisos de visualització d'imatges",
    es = u"Permisos de visualización de imágenes",
    en = u"Render permissions"
)

translations.define("RenderPermission.image_factories",
    ca = u"Processat",
    es = u"Procesado",
    en = u"Processing"
)

translations.define("RenderPermission.image_factories-explanation",
    ca = u"Limita el permís o prohibició a un subconjunt de les diferents "
         u"visualitzacions suportades pel lloc web.",
    es = u"Limita el permiso o prohibición a un subconjunto de las distintas "
         u"visualizaciones soportadas por el sitio web.",
    en = u"Limits the permission to a specific subset of the different "
         u"renderings supported by the site."
)

# MemberPermission
#------------------------------------------------------------------------------
translations.define("MemberPermission",
    ca = u"Permís de membre",
    es = u"Permiso de miembro",
    en = u"Member permission"
)

translations.define("MemberPermission-plural",
    ca = u"Permisos sobre els membres",
    es = u"Permisos sobre los miembros",
    en = u"Member permissions"
)

translations.define("MemberPermission.matching_members",
    ca = u"Membres inclosos",
    es = u"Miembros incluidos",
    en = u"Included members"
)

# ReadMemberPermission
#------------------------------------------------------------------------------
translations.define("ReadMemberPermission",
    ca = u"Permís de lectura de membres",
    es = u"Permiso de lectura de miembros",
    en = u"Read members permission"
)

translations.define("ReadMemberPermission-plural",
    ca = u"Permisos de lectura de membres",
    es = u"Permisos de lectura de miembros",
    en = u"Read members permissions"
)

# ModifyMemberPermission
#------------------------------------------------------------------------------
translations.define("ModifyMemberPermission",
    ca = u"Permís de modificació de membres",
    es = u"Permiso de modificación de miembros",
    en = u"Modify members permission"
)

translations.define("ModifyMemberPermission-plural",
    ca = u"Permisos de lectura de membres",
    es = u"Permisos de lectura de miembros",
    en = u"Read members permissions"
)

# TranslationPermission
#------------------------------------------------------------------------------
translations.define("TranslationPermission",
    ca = u"Permís de traducció",
    es = u"Permiso de traducción",
    en = u"Translation permission"
)

translations.define("TranslationPermission-plural",
    ca = u"Permisos de traducció",
    es = u"Permisos de traducción",
    en = u"Translation permissions"
)

translations.define("TranslationPermission.matching_languages",
    ca = u"Idiomes inclosos",
    es = u"Idiomas incluidos",
    en = u"Included languages"
)

# ReadTranslationPermission
#------------------------------------------------------------------------------
translations.define("ReadTranslationPermission",
    ca = u"Permís de lectura de traducció",
    es = u"Permiso de lectura de traducción",
    en = u"Read translation permission"
)

translations.define("ReadTranslationPermission-plural",
    ca = u"Permisos de lectura de traducció",
    es = u"Permisos de lectura de traducción",
    en = u"Read translation permissions"
)

# CreateTranslationPermission
#------------------------------------------------------------------------------
translations.define("CreateTranslationPermission",
    ca = u"Permís de creació de traducció",
    es = u"Permiso de creación de traducción",
    en = u"Create translation permission"
)

translations.define("CreateTranslationPermission-plural",
    ca = u"Permisos de creació de traducció",
    es = u"Permisos de creación de traducción",
    en = u"Create translation permissions"
)

# ModifyTranslationPermission
#------------------------------------------------------------------------------
translations.define("ModifyTranslationPermission",
    ca = u"Permís de modificació de traducció",
    es = u"Permiso de modificación de traducción",
    en = u"Modify translation permission"
)

translations.define("ModifyTranslationPermission-plural",
    ca = u"Permisos de modificació de traducció",
    es = u"Permisos de modificación de traducción",
    en = u"Modify translation permissions"
)

# DeleteTranslationPermission
#------------------------------------------------------------------------------
translations.define("DeleteTranslationPermission",
    ca = u"Permís d'eliminació de traducció",
    es = u"Permiso de eliminación de traducción",
    en = u"Delete translation permission"
)

translations.define("DeleteTranslationPermission-plural",
    ca = u"Permisos d'eliminació de traducció",
    es = u"Permisos de eliminación de traducción",
    en = u"Delete translation permissions"
)

# ReadHistoryPermission
#------------------------------------------------------------------------------
translations.define("ReadHistoryPermission",
    ca = u"Permís de lectura d'històric",
    es = u"Permiso de lectura de histórico",
    en = u"Read past revisions permission"
)

translations.define("ReadMemberPermission-plural",
    ca = u"Permisos de lectura d'històric",
    es = u"Permisos de lectura de histórico",
    en = u"Read past revisions permissions"
)

# URI
#------------------------------------------------------------------------------
translations.define("URI",
    ca = u"Adreça web",
    es = u"Dirección web",
    en = u"Web address"
)

translations.define("URI-plural",
    ca = u"Adreces web",
    es = u"Direcciones web",
    en = u"Web addresses"
)

translations.define("URI.content",
    ca = u"Contingut",
    es = u"Contenido",
    en = u"Content"
)

translations.define("URI.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("URI.uri",
    ca = u"Adreça",
    es = u"Dirección",
    en = u"Address"
)

translations.define("URI.language_specific_uri",
    ca = u"Adreça per idioma",
    es = u"Dirección por idioma",
    en = u"Language specific address"
)

# Style
#------------------------------------------------------------------------------
translations.define("Style",
    ca = u"Estil",
    es = u"Estilo",
    en = u"Style"
)

translations.define("Style-plural",
    ca = u"Estils",
    es = u"Estilos",
    en = u"Styles"
)

translations.define("Style.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("Style.custom_class_name",
    ca = u"Classe CSS",
    es = u"Clase CSS",
    en = u"CSS class"
)

translations.define("Style.applicable_to_text",
    ca = u"Aplicable al text",
    es = u"Aplicable al texto",
    en = u"Applies to text"
)

translations.define("Style.custom_class_name-explanation",
    ca = u"Permet especificar el nom de la classe CSS resultant. Si no "
         u"s'indica, el sistema decidirà el nom seguint un patró "
         u"incremental.",
    es = u"Permite especificar el nombre de la clase CSS resultante. Si no "
         u"se indica, el sistema decidirá el nombre siguiendo un patrón "
         u"incremental.",
    en = u"Specifies the name of the resulting CSS class. If no name is "
         u"given, the system will choose a name following an incremental "
         u"pattern."
)

translations.define("Style.declarations",
    ca = u"Declaracions CSS",
    es = u"Declaraciones CSS",
    en = u"CSS declarations"
)

translations.define("Style.admin_declarations",
    ca = u"Declaracions CSS per l'administració",
    es = u"Declaraciones CSS para el administrador",
    en = u"Admin CSS declarations"
)

# UserView
#------------------------------------------------------------------------------
translations.define("UserView",
    ca = u"Vista d'usuari",
    es = u"Vista de usuario",
    en = u"User view"
)

translations.define("UserView-plural",
    ca = u"Vistes d'usuari",
    es = u"Vistas de usuario",
    en = u"User views"
)

translations.define("UserView.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("UserView.parameters",
    ca = u"Vista",
    es = u"Vista",
    en = u"View"
)

translations.define("UserView.roles",
    ca = u"Rols",
    es = u"Roles",
    en = u"Roles"
)

# Back office
#------------------------------------------------------------------------------
translations.define("BackOffice",
    ca = u"Gestor de continguts",
    es = u"Gestor de contenidos",
    en = u"Content manager"
)

translations.define("BackOffice-plural",
    ca = u"Gestors de continguts",
    es = u"Gestores de contenidos",
    en = u"Content managers"
)

# File
#------------------------------------------------------------------------------
translations.define("File",
    ca = u"Fitxer",
    es = u"Fichero",
    en = u"File"
)

translations.define("File-plural",
    ca = u"Fitxers",
    es = u"Ficheros",
    en = u"Files"
)

translations.define("File.content",
    ca = u"Contingut",
    es = u"Contenido",
    en = u"Content"
)

translations.define("File.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("File.file_name",
    ca = u"Nom del fitxer",
    es = u"Nombre del fichero",
    en = u"File name"
)

translations.define("File.file_size",
    ca = u"Mida del fitxer",
    es = u"Tamaño de fichero",
    en = u"File size"
)

translations.define("File.local_path",
    ca = u"Fitxer local",
    es = u"Fichero local",
    en = u"Local file"
)

translations.define("File.image_effects",
    ca = u"Efectes",
    es = u"Efectos",
    en = u"Effects"
)

translations.define("BackOfficeEditForm.upload",
    ca = u"Càrrega de fitxer",
    es = u"Carga de fichero",
    en = u"File upload"
)

# News
#------------------------------------------------------------------------------
translations.define("News",
    ca = u"Notícia",
    es = u"Noticia",
    en = u"News"
)

translations.define("News-plural",
    ca = u"Notícies",
    es = u"Noticias",
    en = u"News"
)

translations.define("News-none",    
    es = u"Ninguna"
)

translations.define("News.news_date",
    ca = u"Data de la notícia",
    es = u"Fecha de la noticia",
    en = u"News date"
)

translations.define("News.image",
    ca = u"Imatge",
    es = u"Imagen",
    en = u"Image"
)

translations.define("News.summary",
    ca = u"Sumari",
    es = u"Sumario",
    en = u"Summary"
)

translations.define("News.body",
    ca = u"Cos",
    es = u"Cuerpo",
    en = u"Body"
)

# Event
#------------------------------------------------------------------------------
translations.define("Event",
    ca = u"Esdeveniment",
    es = u"Evento",
    en = u"Event"
)

translations.define("Event-plural",
    ca = u"Esdeveniments",
    es = u"Eventos",
    en = u"Events"
)

translations.define("Event.event_start",
    ca = u"Inici de l'esdeveniment",
    es = u"Inicio del evento",
    en = u"Event start"
)

translations.define("Event.event_end",
    ca = u"Fí de l'esdeveniment",
    es = u"Fin del evento",
    en = u"Event end"
)

translations.define("Event.event_location",
    ca = u"Lloc",
    es = u"Lugar",
    en = u"Place"
)

translations.define("Event.image",
    ca = u"Imatge",
    es = u"Imagen",
    en = u"Image"
)

translations.define("Event.summary",
    ca = u"Sumari",
    es = u"Sumario",
    en = u"Summary"
)

translations.define("Event.body",
    ca = u"Cos",
    es = u"Cuerpo",
    en = u"Body"
)

# Role
#------------------------------------------------------------------------------
translations.define("Role",
    ca = u"Rol",
    es = u"Rol",
    en = u"Role"
)

translations.define("Role-plural",
    ca = u"Rols",
    es = u"Roles",
    en = u"Roles"
)

translations.define("Role.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("Role.users",
    ca = u"Usuaris",
    es = u"Usuarios",
    en = u"Users"
)

translations.define("Role.user_views",
    ca = u"Vistes d'usuari",
    es = u"Vistas de usuario",
    en = u"User views"
)

translations.define("Role.permissions",
    ca = u"Permisos",
    es = u"Permisos",
    en = u"Permissions"
)

translations.define("Role.base_roles",
    ca = u"Rols base",
    es = u"Roles base",
    en = u"Base roles"
)

translations.define("Role.child_roles",
    ca = u"Rols derivats",
    es = u"Roles derivados",
    en = u"Derived roles"
)

translations.define("Role.hidden_content_types",
    ca = u"Tipus ocults",
    es = u"Tipos ocultos",
    en = u"Hidden content types"
)

translations.define("Role.hidden_content_types-explanation",
    ca = u"Una llista de tipus de contingut que no es mostraran a l'usuari. "
         u"Utilitzat per filtrar les entrades del menú principal del gestor.",
    es = u"Una lista de tipos de contenido que no se mostrarán al usuario. "
         u"Utilizado para filtrar las entradas del menú principal del gestor.",
    en = u"A list of content types that will be hidden from the user. Used to "
         u"filter the visible entries in the main menu for the back office "
         u"interface."
)

translations.define("Role.implicit",
    ca = u"Implícit",
    es = u"Implícito",
    en = u"Implicit"
)

# Template
#------------------------------------------------------------------------------
translations.define("Template",
    ca = u"Plantilla",
    es = u"Plantilla",
    en = u"Template"
)

translations.define("Template-plural",
    ca = u"Plantilles",
    es = u"Plantillas",
    en = u"Templates"
)

translations.define("Template-none",
    es = u"Ninguna"
)

translations.define("Template.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("Template.identifier",
    ca = u"Identificador",
    es = u"Identificador",
    en = u"Identifier"
)

translations.define("Template.engine",
    ca = u"Motor de pintat",
    es = u"Motor de pintado",
    en = u"Rendering engine"
)

translations.define("Template.documents",
    ca = u"Documents",
    es = u"Documentos",
    en = u"Documents"
)

# Controller
#------------------------------------------------------------------------------
translations.define("Controller",
    ca = u"Controlador",
    es = u"Controlador",
    en = u"Controller"
)

translations.define("Controller-plural",
    ca = u"Controladors",
    es = u"Controladores",
    en = u"Controllers"
)

translations.define("Controller.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("Controller.python_name",
    ca = u"Implementació",
    es = u"Implementación",
    en = u"Implementation"
)

translations.define("Controller.python_name-explanation",
    ca = u"Nom qualificat de la implementació del controlador en Python",
    es = u"Nombre cualificado de la implementación del controlador en Python",
    en = u"Qualified name of the Python implementation for the controller"
)

# Extension
#------------------------------------------------------------------------------
translations.define("Extension",
    ca = u"Extensió",
    es = u"Extensión",
    en = u"Extension"
)

translations.define("Extension-plural",
    ca = u"Extensions",
    es = u"Extensiones",
    en = u"Extensions"
)

translations.define("Extension.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("Extension.description",
    ca = u"Descripció",
    es = u"Descripción",
    en = u"Description"
)

translations.define("Extension.extension_author",
    ca = u"Autor de l'extensió",
    es = u"Autor de la extensión",
    en = u"Extension author"
)

translations.define("Extension.license",
    ca = u"Llicència",
    es = u"Licencia",
    en = u"License"
)

translations.define("Extension.web_page",
    ca = u"Pàgina web",
    es = u"Página web",
    en = u"Web page"
)

translations.define("Extension.enabled",
    ca = u"Activada",
    es = u"Activada",
    en = u"Enabled"
)

translations.define(
    "woost.controllers.backoffice.ExtensionEditNode "
    "enabled extension needs reloading",
    ca = lambda extension:
        u"L'extensió <strong>%s</strong> s'activarà quan es torni a iniciar "
        u"l'aplicació"
        % translations(extension, "ca"),
    es = lambda extension:
        u"La extensión <strong>%s</strong> se activará cuando se reinicie la "
        u"aplicación"
        % translations(extension, "es"),
    en = lambda extension:
        u"The <strong>%s</strong> will be loaded the next time the "
        u"application starts"
        % translations(extension, "en")
)

translations.define(
    "woost.controllers.backoffice.ExtensionEditNode "
    "disabled extension needs reloading",
    ca = lambda extension:
        u"L'extensió <strong>%s</strong> es desactivarà quan es torni "
        u"a iniciar l'aplicació"
        % translations(extension, "ca"),
    es = lambda extension:
        u"La extensión <strong>%s</strong> se desactivará cuando se reinicie "
        u"la aplicación"
        % translations(extension, "es"),
    en = lambda extension:
        u"The <strong>%s</strong> will be unloaded the next time the "
        u"application restarts"
        % translations(extension, "en")
)

# ChangeSet
#------------------------------------------------------------------------------
translations.define("ChangeSet",
    ca = u"Revisió",
    es = u"Revisión",
    en = u"Revision"
)

translations.define("ChangeSet-plural",
    ca = u"Revisions",
    es = u"Revisiones",
    en = u"Revisions"
)

translations.define("ChangeSet.id",
    ca = u"ID",
    es = u"ID",
    en = u"ID"
)

translations.define("ChangeSet.author",
    ca = u"Autor",
    es = u"Autor",
    en = u"Author"
)

translations.define("ChangeSet.date",
    ca = u"Data",
    es = u"Fecha",
    en = u"Date"
)

translations.define("ChangeSet.changes",
    ca = u"Canvis",
    es = u"Cambios",
    en = u"Changes"
)

# Change
#------------------------------------------------------------------------------
translations.define("Change",
    ca = u"Canvi",
    es = u"Cambio",
    en = u"Change"
)

translations.define("ChangeSet-plural",
    ca = u"Canvis",
    es = u"Cambios",
    en = u"Changes"
)

translations.define("Change.id",
    ca = u"ID",
    es = u"ID",
    en = u"ID"
)

translations.define("Change.changeset",
    ca = u"Revisió",
    es = u"Revisión",
    en = u"Revision"
)

translations.define("Change.action",
    ca = u"Acció",
    es = u"Acción",
    en = u"Action"
)

translations.define("Change.target",
    ca = u"Element",
    es = u"Elemento",
    en = u"Item"
)

translations.define("Change.changed_members",
    ca = u"Membres modificats",
    es = u"Miembros modificados",
    en = u"Modified members"
)

translations.define("Change.item_state",
    ca = u"Estat",
    es = u"Estado",
    en = u"State"
)

def _translate_woost_models_change_instance_ca(action, target):
    
    if isinstance(target, int):
        target_desc = "%d elements" % target
        apostrophe = False
    else:
        target_desc = translations(target, "ca")

        if not target_desc:
            return ""

        apostrophe = target_desc[0].lower() in u"haeiouàèéíòóú"
        target_desc = u"<em>" + target_desc + u"</em>"
    
    action_id = action.identifier

    if action_id == "edit":
        action_desc = u"Edició"
    elif action_id == "create":
        action_desc = u"Creació"
    elif action_id == "delete":
        action_desc = u"Eliminació"
    else:
        return ""
    
    return action_desc + (" d'" if apostrophe else " de ") + target_desc

def _translate_woost_models_change_instance_es(action, target):
    
    if isinstance(target, int):
        target_desc = "%d elementos" % target
    else:
        target_desc = translations(target, "es")

        if not target_desc:
            return ""

        target_desc = u"<em>" + target_desc + u"</em>"
    
    action_id = action.identifier

    if action_id == "edit":
        action_desc = u"Edición"
    elif action_id == "create":
        action_desc = u"Creación"
    elif action_id == "delete":
        action_desc = u"Eliminación"
    else:
        return ""
    
    return action_desc + u" de " + target_desc

def _translate_woost_models_change_instance_en(action, target):
    
    if isinstance(target, int):
        target_desc = "%d items" % target
    else:
        target_desc = translations(target, "ca")

        if not target_desc:
            return ""
        
        target_desc = u"<em>" + target_desc + u"</em>"
    
    action_id = action.identifier

    if action_id == "edit":
        action_desc = u"modified"
    elif action_id == "create":
        action_desc = u"created"
    elif action_id == "delete":
        action_desc = u"deleted"
    else:
        return ""
    
    return target_desc + u" " + action_desc

translations.define("woost.models.changesets.Change description",
    ca = _translate_woost_models_change_instance_ca,
    es = _translate_woost_models_change_instance_es,
    en = _translate_woost_models_change_instance_en
)

translations.define("woost create action",
    ca = u"Creació",    
    es = u"Creación",
    en = u"Creation"
)

translations.define("woost modify action",
    ca = u"Modificació",
    es = u"Modificación",
    en = u"Modification"
)

translations.define("woost delete action",
    ca = u"Eliminació",
    es = u"Eliminación",
    en = u"Eliminació"
)

translations.define(
    "woost.models.userfilter.ChangeSetActionFilter-instance",
    ca = u"Acció",
    es = u"Acción",
    en = u"Action"
)

translations.define(
    "woost.models.userfilter.ChangeSetTargetFilter-instance",
    ca = u"Element",
    es = u"Elemento",
    en = u"Item"
)

translations.define(
    "woost.models.userfilter.ChangeSetTargetTypeFilter-instance",
    ca = u"Tipus d'element",
    es = u"Tipo de elemento",
    en = u"Item type"
)

# Trigger
#------------------------------------------------------------------------------
translations.define("Trigger",
    ca = u"Disparador",
    es = u"Disparador",
    en = u"Trigger"
)

translations.define("Trigger-plural",
    ca = u"Disparadors",
    es = u"Disparadores",
    en = u"Triggers"
)

translations.define("Trigger.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("Trigger.execution_point",
    ca = u"Moment d'execució",
    es = u"Momento de ejecución",
    en = u"Execution point"
)

translations.define("Trigger.batch_execution",
    ca = u"Execució agrupada",
    es = u"Ejecución agrupada",
    en = u"Batch execution"
)

translations.define("Trigger.batch_execution-explanation",
    ca = u"Si s'agrupa l'execució, el disparador només s'activarà un cop per "
         u"transacció, independentment de quantes accions d'aquest tipus "
         u"s'hagin realitzat.",
    es = u"Si se agrupa la ejecución, el disparador solo se activará una vez "
         u"por transacción, sin importar cuantas acciones de este tipo "
         u"se hayan realizado.",
    en = u"If checked, the trigger will be activated only once per "
         u"transaction, regardless of how many times its activation "
         u"conditions are met."
)

translations.define("Trigger.matching_roles",
    ca = u"Rols a observar",
    es = u"Roles a observar",
    en = u"Watched roles"
)

translations.define("Trigger.matching_roles-explanation",
    ca = u"Si no es selecciona cap rol, el disparador s'activarà "
         u"independentment de l'usuari que inicii l'acció.",
    es = u"Si no se selecciona ningún rol, el disparador se activará "
         u"independientemente del usuario que inicie la acción.",
    en = u"If no role is checked, the trigger will execute regardless "
         u"of which user started the action."
)

translations.define("Trigger.condition",
    ca = u"Condició",
    es = u"Condición",
    en = u"Condition"
)

translations.define("Trigger.condition-explanation",
    ca = u"Una expressió en python que determina si s'executa o no el "
         u"disparador.",
    es = u"Una expresión en python que determina si se ejecuta o no el "
         u"disparador.",
    en = u"A python expression that enables or disables the execution of "
         u"the trigger depending on its context."
)

translations.define("Trigger.custom_context",
    ca = u"Context",
    es = u"Contexto",
    en = u"Context"
)

translations.define("Trigger.custom_context-explanation",
    ca = u"Un bloc de codi Python que permet personalitzar els paràmetres "
         u"que es passaran al disparador en el moment en que sigui executat.",
    es = u"Un bloque de código Python que permite personalizar los parámetros "
         u"que recibirá el disparador en el momento en que sea ejecutado.",
    en = u"A block of Python code that allows to customize the parameters "
         u"that the trigger will receive when it is finally executed."
)

translations.define("Trigger.responses",
    ca = u"Respostes",
    es = u"Respuestas",
    en = u"Responses"
)

translations.define("woost.models.Trigger.execution_point before",
    ca = u"Immediatament",
    es = u"Inmediatamente",
    en = u"Immediately"
)

translations.define("woost.models.Trigger.execution_point after",
    ca = u"En confirmar la transacció",
    es = u"Tras confirmar la transacción",
    en = u"After committing the transaction"
)

# ContentTrigger
#------------------------------------------------------------------------------
translations.define("ContentTrigger",
    ca = u"Disparador per elements",
    es = u"Disparador para elementos",
    en = u"Content trigger"
)

translations.define("ContentTrigger-plural",
    ca = u"Disparadors per contingut",
    es = u"Disparadores para contenido",
    en = u"Content triggers"
)

translations.define("ContentTrigger.matching_items",
    ca = u"Elements a observar",
    es = u"Elementos a observar",
    en = u"Watched items"
)

# CreateTrigger
#------------------------------------------------------------------------------
translations.define("CreateTrigger",
    ca = u"Disparador de creació",
    es = u"Disparador de creación",
    en = u"Create trigger"
)

translations.define("CreateTrigger-plural",
    ca = u"Disparadors de creació",
    es = u"Disparadores de creación",
    en = u"Create triggers"
)

# InsertTrigger
#------------------------------------------------------------------------------
translations.define("InsertTrigger",
    ca = u"Disparador d'inserció",
    es = u"Disparador de inserción",
    en = u"Insert trigger"
)

translations.define("InsertTrigger-plural",
    ca = u"Disparadors d'inserció",
    es = u"Disparadores de inserción",
    en = u"Insert triggers"
)

# ModifyTrigger
#------------------------------------------------------------------------------
translations.define("ModifyTrigger",
    ca = u"Disparador de modificació",
    es = u"Disparador de modificación",
    en = u"Modify trigger"
)

translations.define("ModifyTrigger-plural",
    ca = u"Disparadors de modificació",
    es = u"Disparadores de modificación",
    en = u"Modify triggers"
)

translations.define("ModifyTrigger.matching_members",
    ca = u"Membres a observar",
    es = u"Miembros a observar",
    en = u"Watched members"
)

translations.define("ModifyTrigger.matching_members-explanation",
    ca = u"Si no es selecciona cap membre, el disparador s'activarà "
         u"sigui quin sigui el membre modificat.",
    es = u"Si no se selecciona ningún miembro, el disparador se activará "
         u"sea cual sea el miembro modificado.",
    en = u"If no member is checked, the trigger will execute regardless "
         u"of which member is modified."
)

translations.define("ModifyTrigger.matching_languages",
    ca = u"Idiomes a observar",
    es = u"Idiomas a observar",
    en = u"Watched languages"
)

translations.define("ModifyTrigger.matching_languages-explanation",
    ca = u"Si no es selecciona cap idioma, el disparador s'activarà "
         u"sigui quin sigui l'idioma dels valors modificats.",
    es = u"Si no se selecciona ningún idioma, el disparador se activará "
         u"independientemente del idioma de los valores modificados.",
    en = u"If no language is checked, the trigger will execute regardless "
         u"of which language modified values are translated into."
)

translations.define("woost.controllers.DeleteController.node_deleted_notice",
    ca = u"L'element que estaves editant ha estat eliminat.",
    es = u"El elemento que estabas editando ha sido eliminado.",
    en = u"The item you were editing has been deleted"
)

# DeleteTrigger
#------------------------------------------------------------------------------
translations.define("DeleteTrigger",
    ca = u"Disparador d'eliminació",
    es = u"Disparador de eliminación",
    en = u"Delete trigger"
)

translations.define("DeleteTrigger-plural",
    ca = u"Disparadors d'eliminació",
    es = u"Disparadores de eliminación",
    en = u"Delete triggers"
)

# ConfirmDraftTrigger
#------------------------------------------------------------------------------
translations.define("ConfirmDraftTrigger",
    ca = u"Disparador de confirmació d'esborrany",
    es = u"Disparador de confirmación de borrador",
    en = u"Draft confirmation trigger"
)

translations.define("ConfirmDraftTrigger-plural",
    ca = u"Disparadors de confirmació d'esborrany",
    es = u"Disparadores de confirmación de borrador",
    en = u"Draft confirmation triggers"
)

# TriggerResponse
#------------------------------------------------------------------------------
translations.define("TriggerResponse",
    ca = u"Resposta",
    es = u"Respuesta",
    en = u"Trigger response"
)

translations.define("TriggerResponse-plural",
    ca = u"Respostes",
    es = u"Respuestas",
    en = u"Trigger responses"
)

# CustomTriggerResponse
#------------------------------------------------------------------------------
translations.define("CustomTriggerResponse",
    ca = u"Resposta personalitzada",
    es = u"Respuesta personalizada",
    en = u"Custom response"
)

translations.define("CustomTriggerResponse-plural",
    ca = u"Respostes personalitzades",
    es = u"Respuestas personalizadas",
    en = u"Custom responses"
)

translations.define("CustomTriggerResponse.code",
    ca = u"Codi de resposta",
    es = u"Código de respuesta",
    en = u"Response code"
)

# SendEmailTriggerResponse
#------------------------------------------------------------------------------
translations.define("SendEmailTriggerResponse",
    ca = u"Enviament de correu electrònic",
    es = u"Envío de correo electrónico",
    en = u"Send E-mail"
)

translations.define("SendEmailTriggerResponse-plural",
    ca = u"Enviaments de correu electrònic",
    es = u"Envíos de correo electrónico",
    en = u"Send E-mail"
)

translations.define("SendEmailTriggerResponse.email_template",
    ca = u"Plantilla de correu electrònic",
    es = u"Plantilla de correo electrónico",
    en = u"E-mail template"
)

# EmailTemplate
#------------------------------------------------------------------------------ 
translations.define("EmailTemplate",
    ca = u"Plantilla de correu electrònic",
    es = u"Plantilla de correo electrónico",
    en = u"E-mail template"
)

translations.define("EmailTemplate-plural",
    ca = u"Plantilles de correu electrònic",
    es = u"Plantillas de correo electrónico",
    en = u"E-mail templates"
)

translations.define("EmailTemplate.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("EmailTemplate.mime_type",
    ca = u"Tipus MIME",
    es = u"Tipo MIME",
    en = u"MIME type"
)

translations.define("EmailTemplate.sender",
    ca = u"Remitent",
    es = u"Remitente",
    en = u"Sender"
)

translations.define("EmailTemplate.receivers",
    ca = u"Destinataris",
    es = u"Destinatarios",
    en = u"Receivers"
)

translations.define("EmailTemplate.bcc",
    ca = u"Còpia oculta",
    es = u"Copia oculta",
    en = u"Blind carbon copy"
)

translations.define("EmailTemplate.template_engine",
    ca = u"Motor de pintat",
    es = u"Motor de pintado",
    en = u"Rendering engine"
)

translations.define("EmailTemplate.subject",
    ca = u"Assumpte",
    es = u"Asunto",
    en = u"Subject"
)

translations.define("EmailTemplate.body",
    ca = u"Cos del missatge",
    es = u"Cuerpo del mensaje",
    en = u"Message body"
)

translations.define("EmailTemplate.initialization_code",
    ca = u"Codi d'inicialització",
    es = u"Código de inicialización",
    en = u"Initialization code"
)

translations.define("EmailTemplate.initialization_code-explanation",
    ca = u"Un bloc de codi Python que permet modificar el context que es "
         u"facilita a la resta de camps durant la construcció del missatge "
         u"(útil per definir variables complexes i valors comuns a diferents "
         u"camps o traduccions).",
    es = u"Un bloque de código Python que permite modificar el contexto que "
         u"se facilita al resto de campos durante la construcción del "
         u"mensaje (útil para definir variables complejas o valores comunes a "
         u"distintos campos o traducciones).",
    en = u"A block of Python code that makes it possible to modify the "
         u"context supplid to the other fields when the message is "
         u"constructed (useful in order to more comfortably define complex "
         u"variables or values that must be shared across fields or "
         u"translations)."
)

# Feed
#------------------------------------------------------------------------------
translations.define("Feed",
    ca = u"Canal de sindicació",
    es = u"Canal de sindicación",
    en = u"Syndication feed"
)

translations.define("Feed-plural",
    ca = u"Canals de sindicació",
    es = u"Canales de sindicación",
    en = u"Syndication feeds"
)

translations.define("Feed.feed_items",
    ca = u"Elements llistats",
    es = u"Elementos listados",
    en = u"Listed elements"
)

translations.define("Feed.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("Feed.ttl",
    ca = u"Temps d'expiració (TTL)",
    es = u"Tiempo de expiración (TTL)",
    en = u"TTL"
)

translations.define("Feed.image",
    ca = u"Imatge",
    es = u"Imagen",
    en = u"Image"
)

translations.define("Feed.description",
    ca = u"Descripció",
    es = u"Descripción",
    en = u"Description"
)

translations.define("Feed.limit",
    ca = u"Límit d'elements publicats",
    es = u"Límite de elementos publicados",
    en = u"Published items limit"
)

translations.define("Feed.query_parameters",
    ca = u"Elements publicats",
    es = u"Elementos publicados",
    en = u"Published items"
)

translations.define("Feed.item_title_expression",
    ca = u"Expressió pel títol dels elements",
    es = u"Expresión para el título de los elementos",
    en = u"Item title expression"
)

translations.define("Feed.item_link_expression",
    ca = u"Expressió per l'enllaç dels elements",
    es = u"Expresión para el enlace de los elementos",
    en = u"Item link expression"
)

translations.define("Feed.item_publication_date_expression",
    ca = u"Expressió per la data de publicació dels elements",
    es = u"Expresión para la fecha de publicación de los elementos",
    en = u"Item publication date expression"
)

translations.define("Feed.item_description_expression",
    ca = u"Expressió per la descripció dels elements",
    es = u"Expresión para la descripción de los elementos",
    en = u"Item description expression"
)

# ContentTypePicker
#------------------------------------------------------------------------------
translations.define("woost.views.ContentTypePicker select",
    ca = u"Seleccionar",
    es = u"Seleccionar",
    en = u"Select"
)

translations.define("woost.views.ContentTypePicker accept",
    ca = u"Acceptar",
    es = u"Aceptar",
    en = u"Accept"
)

translations.define("woost.views.ContentTypePicker cancel",
    ca = u"Cancel·lar",
    es = u"Cancelar",
    en = u"Cancel"
)

translations.define("woost.views.ContentTypePicker.empty_label",
    ca = u"Cap",
    es = u"Ninguno",
    en = u"None"
)

# Preview
#------------------------------------------------------------------------------
translations.define("woost.backoffice invalid item preview",
    ca = u"Algun camp del formulari no té un format correcte. "
         u"No es pot realitzar la vista prèvia.",
    es = u"Algún campo del formulario no tiene un formato correcto. "
         u"No se puede realizar la vista previa.",
    en = u"Some form field has no correct format. "
         u"Impossible to render preview."
)

translations.define("woost.views.BackOfficePreviewView preview language",
    ca = u"Idioma de la visualització:",
    es = u"Idioma de la visualización:",
    en = u"Visualization language:"
)

# Expressions
#------------------------------------------------------------------------------
translations.define(
    "woost.models.publishable.IsPublishedExpression-instance",
    ca = u"publicat",
    es = u"publicado",
    en = u"published"
)

translations.define(
    "woost.models.publishable.IsAccessibleExpression-instance",
    ca = u"accessible",
    es = u"accesible",
    en = u"accessible"
)

translations.define(
    "woost.models.expressions.OwnershipExpression-instance",
    ca = u"propietat de l'usuari actiu",
    es = u"propiedad del usuario activo",
    en = u"owned by the active user"
)

# PasswordChange
#------------------------------------------------------------------------------
translations.define(
    "woost.controllers.passwordchangecontroller.request_sended_notification_message",
    ca = u"""Hem enviat un correu electrònic a l'adreça indicada amb les
        instruccions per reestablir la contrasenya.""",        
    es = u"""Hemos enviado un correo electrónico a la dirección indicada con
        las instrucciones para reestablecer tu contraseña.""",
    en = u"""We have sent an e-mail message to the indicated account 
        containing further instructions to reset your password."""
)

translations.define(
    "woost.controllers.passwordchangecontroller.confirmation_message",
    ca = u"Canvi de contrasenya realitzat correctament.",
    es = u"Cambio de contraseña realizado correctamente.",
    en = u"Password correctly changed."
)

translations.define(
    "woost.controllers.passwordchangecontroller."
    "UserIdentifierNotRegisteredError-instance",
    ca = u"No existeix cap usuari amb aquest identificador",
    es = u"No existe ningún usuario registrado con este identificador",
    en = u"There is no user with the indicated identifier"
)

translations.define(
    "woost.controllers.passwordchangecontroller."
    "UserEmailMissingError-instance",
    ca = u"L'usuari que has indicat no té cap adreça de correu electrònic "
         u"associada: no es pot canviar la seva contrasenya a través "
         u"d'aquest formulari.",
    es = u"El usuario que has indicado no tiene ninguna dirección de "
         u"correo electrónico asociada: no se puede cambiar su contraseña a "
         u"través de este formulario.",
    en = u"The user you indicated has no known e-mail address. Only users "
         u"with verified e-mail addresses can use this form to change their "
         u"password."
)

translations.define(
    "PasswordChangeConfirmationForm.password_confirmation",
    ca = u"Confirmar la contrasenya",
    es = u"Confirmar la contraseña",
    en = u"Confirm password"
)

# EditPanel
#------------------------------------------------------------------------------
translations.define("woost.views.EditPanel.show_panel_button",
    ca = u"Mostrar panell d'edició",
    es = u"Mostrar panel de edición",
    en = u"Show edit panel"
)

translations.define("woost.views.EditPanel.close_panel_button",
    ca = u"Ocultar panell d'edició",
    es = u"Ocultar panel de edición",
    en = u"Close edit panel"
)

translations.define("woost.views.EditPanel.actions_title",
    ca = u"Accions",
    es = u"Acciones",
    en = u"Actions"
)

# Renderer
#------------------------------------------------------------------------------
translations.define("Renderer",
    ca = u"Pintador d'imatges",
    es = u"Pintador de imágenes",
    en = u"Renderer"
)

translations.define("Renderer-plural",
    ca = u"Pintadors d'imatges",
    es = u"Pintadores de imágenes",
    en = u"Renderers"
)

translations.define("Renderer.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

# ImageFileRenderer
#------------------------------------------------------------------------------
translations.define("ImageFileRenderer",
    ca = u"Pintador de fitxers d'imatge",
    es = u"Pintador de ficheros de imagen",
    en = u"Image file renderer"
)

translations.define("ImageFileRenderer-plural",
    ca = u"Pintadors de fitxers d'imatge",
    es = u"Pintadores de ficheros de imagen",
    en = u"Image file renderers"
)

translations.define("ImageFileRenderer.max_size",
    ca = u"Mida màxima",
    es = u"Tamaño máximo",
    en = u"Max size"
)

translations.define("ImageFileRenderer.max_size-explanation",
    ca = u"Evita que el servidor processi imatges amb una mida excessiva. "
         u"La mida màxima a processar s'ha d'indicar amb dos valors enters, "
         u"separats per un caràcter 'x' (per exemple, 2000 x 1500). Les "
         u"mides es validaran en orientació vertical o horitzontal, "
         u"indistintament.",
    es = u"Evita que el servidor procese imágenes con un tamaño excesivo. "
         u"El tamaño máximo admisible debe indicarse con dos valores "
         u"enteros, separados por un carácter 'x' (por ejemplo, 2000 x "
         u"1500). El tamaño se validará en orientación vertical o "
         u"horizontal, indistintamente.",
    en = u"Prevents the server from processing excessively large images. The "
         u"maximum image size allowed has to be indicated as a tuple of two "
         u"integers, separated by an 'x' character (ie. 2000 x 1500). Images "
         u"will be validated against this size constraint in both landscape "
         u"and portrait orientations."
)

# IconRenderer
#------------------------------------------------------------------------------
translations.define("IconRenderer",
    ca = u"Llibreria de icones",
    es = u"Librería de iconos",
    en = u"Icon library"
)

translations.define("IconRenderer-plural",
    ca = u"Llibreries de icones",
    es = u"Librerías de iconos",
    en = u"Icon libraries"
)

translations.define("IconRenderer.icon_size",
    ca = u"Mida de les icones",
    es = u"Tamaño de los iconos",
    en = u"Icon size"
)

# HTMLRenderer
#------------------------------------------------------------------------------
translations.define("HTMLRenderer",
    ca = u"Pintador de documents HTML",
    es = u"Pintador de documentos HTML",
    en = u"HTML renderer"
)

translations.define("HTMLRenderer-plural",
    ca = u"Pintadors de documents HTML",
    es = u"Pintadores de documentos HTML",
    en = u"HTML renderers"
)

# ImageURIRenderer
#------------------------------------------------------------------------------
translations.define("ImageURIRenderer",
    ca = u"Pintador d'imatges remotes",
    es = u"Pintador de imágenes remotas",
    en = u"Image URI renderer"
)

translations.define("ImageURIRenderer-plural",
    ca = u"Pintadors d'imatges remotes",
    es = u"Pintadores de imágenes remotas",
    en = u"Image URI renderers"
)

# PDFRenderer
#------------------------------------------------------------------------------
translations.define("PDFRenderer",
    ca = u"Pintador de documents PDF",
    es = u"Pintador de documentos PDF",
    en = u"PDF renderer"
)

translations.define("PDFRenderer-plural",
    ca = u"Pintadors de documents PDF",
    es = u"Pintadores de documentos PDF",
    en = u"PDF renderers"
)

translations.define("PDFRenderer.command",
    ca = u"Comanda",
    es = u"Comando",
    en = u"Command"
)

translations.define("PDFRenderer.timeout",
    ca = u"Temps màxim d'execució",
    es = u"Tiempo máximo de ejecución",
    en = u"Timeout"
)

translations.define("PDFRenderer.timeout_size_factor",
    ca = u"Temps de gràcia segons la mida del fitxer",
    es = u"Tiempo de gracia según el tamaño del fichero",
    en = u"Timeout file size factor"
)

# VideoFileRenderer
#------------------------------------------------------------------------------
translations.define("VideoFileRenderer",
    ca = u"Pintador de fitxers de vídeo",
    es = u"Pintador de ficheros de video",
    en = u"Video file renderer"
)

translations.define("VideoFileRenderer-plural",
    ca = u"Pintadors de fitxers de vídeo",
    es = u"Pintadores de ficheros de video",
    en = u"Video file renderers"
)

# ChainRenderer
#------------------------------------------------------------------------------
translations.define("ChainRenderer",
    ca = u"Pintador en cadena",
    es = u"Pintador en cadena",
    en = u"Chain renderer"
)

translations.define("ChainRenderer-plural",
    ca = u"Pintadors en cadena",
    es = u"Pintadores en cadena",
    en = u"Chain renderers"
)

translations.define("ChainRenderer.renderers",
    ca = u"Pintadors",
    es = u"Pintadores",
    en = u"Renderers"
)

# ImageFactory
#------------------------------------------------------------------------------
translations.define("ImageFactory",
    ca = u"Processador d'imatges",
    es = u"Procesador de imágenes",
    en = u"Image factory"
)

translations.define("ImageFactory-plural",
    ca = u"Processadors d'imatges",
    es = u"Procesadores de imágenes",
    en = u"Image factories"
)

translations.define("ImageFactory.title",
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("ImageFactory.identifier",
    ca = u"Identificador",
    es = u"Identificador",
    en = u"Identifier"
)

translations.define("ImageFactory.identifier-explanation",
    ca = u"Un valor únic que permet accedir al processador programàticament",
    es = u"Un valor único que permite acceder al procesador "
         u"programáticamente",
    en = u"A unique value that makes it possible to access the image factory "
         u"programmatically"
)

translations.define("ImageFactory.renderer",
    ca = u"Pintador",
    es = u"Pintador",
    en = u"Renderer"
)

translations.define("ImageFactory.renderer-explanation",
    ca = u"Especifica la manera en que s'obté la imatge",
    es = u"Especifica la manera en que se obtiene la imagen",
    en = u"Determines the source of produced images"
)

translations.define("ImageFactory.default_format",
    ca = u"Format d'imatge",
    es = u"Formato de imagen",
    en = u"Image format"
)

translations.define("ImageFactory.effects",
    ca = u"Efectes",
    es = u"Efectos",
    en = u"Effects"
)

translations.define("ImageFactory.fallback",
    ca = u"Processador alternatiu",
    es = u"Procesador alternativo",
    en = u"Fallback"
)

translations.define("ImageFactory.fallback-explanation",
    ca = u"Si el processador és incapaç de produïr una imatge, "
         u"es provarà d'obtenir una imatge substitutiva utilitzant "
         u"el processador alternatiu indicat",
    es = u"Si el procesador es incapaz de producir una imagen, se "
         u"intentará obtener una imagen sustitutiva utilizando el "
         u"procesador alternativo indicado",
    en = u"If the image factory fails to produce an image, it will try to "
         u"fall back to the indicated factory to produce an alternative image"
)

# ImageEffect
#------------------------------------------------------------------------------
translations.define("ImageEffect",
    ca = u"Efecte d'imatge",
    es = u"Efecto de imagen",
    en = u"Image effect"
)

translations.define("ImageEffect-plural",
    ca = u"Efectes d'imatge",
    es = u"Efectos de imagen",
    en = u"Image effects"
)

translations.define(
    "woost.models.rendering.horizontal_alignment=left",
    ca = u"Esquerra",
    es = u"Izquierda",
    en = u"Left"
)

translations.define(
    "woost.models.rendering.horizontal_alignment=center",
    ca = u"Centrat",
    es = u"Centrado",
    en = u"Center"
)

translations.define(
    "woost.models.rendering.horizontal_alignment=right",
    ca = u"Dreta",
    es = u"Derecha",
    en = u"Right"
)

translations.define(
    "woost.models.rendering.vertical_alignment=top",
    ca = u"A dalt",
    es = u"Arriba",
    en = u"Top"
)

translations.define(
    "woost.models.rendering.vertical_alignment=center",
    ca = u"Centrat",
    es = u"Centrado",
    en = u"Center"
)

translations.define(
    "woost.models.rendering.vertical_alignment=bottom",
    ca = u"A baix",
    es = u"Abajo",
    en = u"Bottom"
)

# Thumbnail
#------------------------------------------------------------------------------
translations.define("Thumbnail",
    ca = u"Redimensionar",
    es = u"Redimensionar",
    en = u"Thumbnail"
)

translations.define("Thumbnail.width",
    ca = u"Amplada",
    es = u"Ancho",
    en = u"Width"
)

translations.define("Thumbnail.height",
    ca = u"Alçada",
    es = u"Alto",
    en = u"Height"
)

# Crop
#------------------------------------------------------------------------------
translations.define("Crop",
    ca = u"Retallar",
    es = u"Recortar",
    en = u"Crop"
)

translations.define("Crop.left",
    ca = u"X1",
    es = u"X1",
    en = u"X1"
)

translations.define("Crop.top",
    ca = u"Y1",
    es = u"Y1",
    en = u"Y1"
)

translations.define("Crop.right",
    ca = u"X2",
    es = u"X2",
    en = u"X2"
)

translations.define("Crop.bottom",
    ca = u"Y2",
    es = u"Y2",
    en = u"Y2"
)

# Fill
#------------------------------------------------------------------------------
translations.define("Fill",
    ca = u"Redimensionar i retallar",
    es = u"Redimensionar y recortar",
    en = u"Thumbnail and crop"
)

translations.define("Fill.width",
    ca = u"Amplada",
    es = u"Ancho",
    en = u"Width"
)

translations.define("Fill.height",
    ca = u"Alçada",
    es = u"Alto",
    en = u"Height"
)

translations.define("Fill.horizontal_alignment",
    ca = u"Alineament horitzontal",
    es = u"Alineamiento horizontal",
    en = u"Horizontal alignment"
)

translations.define("Fill.vertical_alignment",
    ca = u"Alineament vertical",
    es = u"Alineamiento vertical",
    en = u"Vertical alignment"
)

translations.define("Fill.preserve_vertical_images",
    ca = u"Preservar imatges verticals",
    es = u"Preservar imágenes verticales",
    en = u"Preserve vertical images"
)

# Rotate
#------------------------------------------------------------------------------
translations.define("Rotate",
    ca = u"Rotar",
    es = u"Rotar",
    en = u"Rotate"
)

translations.define("Rotate.angle",
    ca = u"Angle",
    es = u"Ángulo",
    en = u"Angle"
)

# Color
#------------------------------------------------------------------------------
translations.define("Color",
    ca = u"Intensitat del color",
    es = u"Intensidad del color",
    en = u"Color intensity"
)

translations.define("Color.level",
    ca = u"Nivell",
    es = u"Nivel",
    en = u"Level"
)

# Brightness
#------------------------------------------------------------------------------
translations.define("Brightness",
    ca = u"Lluminositat",
    es = u"Luminosidad",
    en = u"Brightness"
)

translations.define("Brightness.level",
    ca = u"Nivell",
    es = u"Nivel",
    en = u"Level"
)

# Contrast
#------------------------------------------------------------------------------
translations.define("Contrast",
    ca = u"Contrast",
    es = u"Contraste",
    en = u"Contrast"
)

translations.define("Contrast.level",
    ca = u"Nivell",
    es = u"Nivel",
    en = u"Level"
)

# Sharpness
#------------------------------------------------------------------------------
translations.define("Sharpness",
    ca = u"Definició",
    es = u"Definición",
    en = u"Sharpness"
)

translations.define("Sharpness.level",
    ca = u"Nivell",
    es = u"Nivel",
    en = u"Level"
)

# Frame
#------------------------------------------------------------------------------
translations.define("Frame",
    ca = u"Marc",
    es = u"Marco",
    en = u"Frame"
)

translations.define("Frame.edge_width",
    ca = u"Gruix del marc",
    es = u"Grueso del marco",
    en = u"Edge width"
)

translations.define("Frame.edge_color",
    ca = u"Color del marc",
    es = u"Color del marco",
    en = u"Edge color"
)

translations.define("Frame.vertical_padding",
    ca = u"Espaiat vertical",
    es = u"Espaciado vertical",
    en = u"Vertical padding"
)

translations.define("Frame.horizontal_padding",
    ca = u"Espaiat horitzontal",
    es = u"Espaciado horizontal",
    en = u"Horizontal padding"
)

translations.define("Frame.background",
    ca = u"Color de fons",
    es = u"Color de fondo",
    en = u"Background"
)

# Shadow
#------------------------------------------------------------------------------
translations.define("Shadow",
    ca = u"Ombra",
    es = u"Sombra",
    en = u"Shadow"
)

translations.define("Shadow.offset",
    ca = u"Desplaçament",
    es = u"Desplazamiento",
    en = u"Offset"
)

translations.define("Shadow.padding",
    ca = u"Espaiat",
    es = u"Espaciado",
    en = u"Padding"
)

translations.define("Shadow.color",
    ca = u"Color",
    es = u"Color",
    en = u"Color"
)

# ReducedOpacity
#------------------------------------------------------------------------------
translations.define("ReducedOpacity",
    ca = u"Reduïr l'opacitat",
    es = u"Reducir la opacidad",
    en = u"Reduce opacity"
)

translations.define("ReducedOpacity.level",
    ca = u"Nivell",
    es = u"Nivel",
    en = u"Level"
)

# Watermark
#------------------------------------------------------------------------------
translations.define("Watermark",
    ca = u"Marca d'aigua",
    es = u"Marca de agua",
    en = u"Watermark"
)

translations.define("Watermark.mark",
    ca = u"Marca",
    es = u"Marca",
    en = u"Mark"
)

translations.define("Watermark.opacity",
    ca = u"Opacitat",
    es = u"Opacidad",
    en = u"Opacity"
)

translations.define("Watermark.placement",
    ca = u"Posicionament",
    es = u"Posicionamiento",
    en = u"Positioning"
)

translations.define("Watermark.placement=middle",
    ca = u"Centrat",
    es = u"Centrado",
    en = u"In the middle"
)

translations.define("Watermark.placement=scale",
    ca = u"Omplir",
    es = u"Rellenar",
    en = u"Scale"
)

translations.define("Watermark.placement=tile",
    ca = u"Repetir",
    es = u"Repetir",
    en = u"Tile"
)

# Flip
#------------------------------------------------------------------------------
translations.define("Flip",
    ca = u"Capgirar",
    es = u"Voltear",
    en = u"Flip"
)

translations.define("Flip.axis",
    ca = u"Eix",
    es = u"Eje",
    en = u"Axis"
)

translations.define("Flip.axis=horizontal",
    ca = u"Horitzontal",
    es = u"Horizontal",
    en = u"Horizontal"
)

translations.define("Flip.axis=vertical",
    ca = u"Vertical",
    es = u"Vertical",
    en = u"Vertical"
)

# Align
#------------------------------------------------------------------------------
translations.define("Align",
    ca = u"Alinear",
    es = u"Alinear",
    en = u"Align"
)

translations.define("Align.width",
    ca = u"Amplada",
    es = u"Ancho",
    en = u"Width"
)

translations.define("Align.height",
    ca = u"Alçada",
    es = u"Alto",
    en = u"Height"
)

translations.define("Align.horizontal_alignment",
    ca = u"Alineament horitzontal",
    es = u"Alineamiento horizontal",
    en = u"Horizontal alignment"
)

translations.define("Align.vertical_alignment",
    ca = u"Alineament vertical",
    es = u"Alineamiento vertical",
    en = u"Vertical alignment"
)

translations.define("Align.background",
    ca = u"Color de fons",
    es = u"Color de fondo",
    en = u"Background"
)

# Grayscale
#------------------------------------------------------------------------------
translations.define("Grayscale",
    ca = u"Tons de gris",
    es = u"Tonos de gris",
    en = u"Grayscale"
)

# Agreement to terms & conditions
#------------------------------------------------------------------------------
translations.define("woost.controllers.formagreement",
    ca = lambda member:
        u"He llegit i accepto "
        u"<a href='%s' target='_blank'>els termes i condicions</a> "
        u"d'aquest formulari"
        % member.agreement_document.get_uri(),
    es = lambda member:
        u"He leído y acepto "
        u"<a href='%s' target='_blank'>los términos y condiciones</a> "
        u"de este formulario"
        % member.agreement_document.get_uri(),
    en = lambda member:
        u"I have read and agree to the "
        u"<a href='%s' target='_blank'>terms and conditions</a> "
        u"of this form"
        % member.agreement_document.get_uri()
)

translations.define(
    "woost.controllers.formagreement.ConsentNotGivenError-instance",
    ca = lambda instance:
        u"Has d'acceptar <a href='%s' target='_blank'>els termes i "
        u"condicions</a> del formulari" 
        % instance.member.agreement_document.get_uri(),
    es = lambda instance:
        u"Debes aceptar <a href='%s' target='_blank'>los términos y "
        u"condiciones</a> de este formulario"
        % instance.member.agreement_document.get_uri(),
    en = lambda instance:
        u"You must accept the <a href='%s' target='_blank'>terms & conditions "
        u"</a> of the form"
        % instance.member.agreement_document.get_uri()
)

# BackOfficeItemHeading
#------------------------------------------------------------------------------
translations.define("woost.views.BackOfficeItemHeading.item_path.conjunction",
    ca = u"a",
    es = u"en",
    en = u"in"
)

# VideoPlayerSettings
#------------------------------------------------------------------------------
translations.define("VideoPlayerSettings", 
    ca = u"Opcions de reproductor de vídeo",
    es = u"Opciones de reproductor de video",
    en = u"Video player settings"
)

translations.define("VideoPlayerSettings-plural", 
    ca = u"Opcions de reproductor de vídeo",
    es = u"Opciones de reproductor de video",
    en = u"Video player settings"
)

translations.define("VideoPlayerSettings.title", 
    ca = u"Nom",
    es = u"Nombre",
    en = u"Name"
)

translations.define("VideoPlayerSettings.width", 
    ca = u"Amplada",
    es = u"Ancho",
    en = u"Width"
)

translations.define("VideoPlayerSettings.height", 
    ca = u"Alçada",
    es = u"Alto",
    en = u"Height"
)

translations.define("VideoPlayerSettings.autoplay",
    ca = u"Iniciar la reproducció automàticament",
    es = u"Iniciar la reproducción automáticamente",
    en = u"Autoplay"
)

translations.define("VideoPlayerSettings.show_player_controls",
    ca = u"Mostrar controls de reproducció",
    es = u"Mostrar controles de reproducción",
    en = u"Show player controls"
)

