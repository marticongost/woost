#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import translations
from cocktail.translations.helpers import ca_possessive

translations.define("Action edit_blocks",
    ca = u"Editar blocs",
    es = u"Editar bloques",
    en = u"Edit blocks"
)

translations.define("woost.extensions.blocks.slots.blocks",
    ca = u"Blocs",
    es = u"Bloques",
    en = u"Blocks"
)

translations.define(
    "woost.extensions.blocks.editblocksnode.EditBlocksNode-instance",
    ca = lambda instance: 
        u"Editant els blocs " + ca_possessive(translations(instance.item)),
    es = lambda instance:
        u"Editando los bloques de " + translations(instance.item),
    en = lambda instance:
        u"Editing the blocks for " + translations(instance.item)
)

# Site
#------------------------------------------------------------------------------
translations.define("Site.common_blocks",
    ca = u"Blocs comuns",
    es = u"Bloques comunes",
    en = u"Common blocks"
)

# BlocksPage
#------------------------------------------------------------------------------
translations.define("BlocksPage",
    ca = u"Pàgina de blocs",
    es = u"Página de bloques",
    en = u"Blocks page"
)

translations.define("BlocksPage-plural",
    ca = u"Pàgines de blocs",
    es = u"Páginas de bloques",
    en = u"Blocks pages"
)

translations.define("BlocksPage.blocks",
    ca = u"Blocs",
    es = u"Bloques",
    en = u"Blocks"
)

# Blocks page template
#------------------------------------------------------------------------------
translations.define("woost.extensions.blocks.blocks_page_template.title",
    ca = u"Plantilla pàgina de blocs",
    es = u"Plantilla página de bloques",
    en = u"Blocks page template"
)

# Block
#------------------------------------------------------------------------------
translations.define("Block",
    ca = u"Bloc",
    es = u"Bloque",
    en = u"Block"
)

translations.define("Block-plural",
    ca = u"Blocs",
    es = u"Bloques",
    en = u"Blocks"
)

translations.define("Block.content",
    ca = u"Contingut",
    es = u"Contenido",
    en = u"Content"
)

translations.define("Block.html",
    ca = u"HTML",
    es = u"HTML",
    en = u"HTML"
)

translations.define("Block.title",
    ca = u"Títol",
    es = u"Título",
    en = u"Title"
)

translations.define("Block.title-explanation",
    ca = u"Descripció del bloc, d'ús intern pels editors",
    es = u"Descripción del bloque, de uso interno para los editores",
    en = u"Description for this block, used internally by editors"
)

translations.define("Block.heading",
    ca = u"Encapçalament",
    es = u"Encabezado",
    en = u"Heading"
)

translations.define("Block.heading-explanation",
    ca = u"Títol del bloc, tal com es mostrarà al web",
    es = u"Título del bloque, tal como se mostraré en la web",
    en = u"Block title, as shown on the website"
)

translations.define("Block.heading_type",
    ca = u"Tipus d'encapçalament",
    es = u"Tipo de encabezado",
    en = u"Heading type"
)

translations.define("Block.heading_type=generic",
    ca = u"Etiqueta genèrica",
    es = u"Etiqueta genérica",
    en = u"Generic label"
)

for level in range(1, 7):
    translations.define("Block.heading_type=h" + str(level),
        ca = u"H" + str(level),
        es = u"H" + str(level),
        en = u"H" + str(level)
    )

translations.define("Block.html_attributes",
    ca = u"Atributs HTML",
    es = u"Atributos HTML",
    en = u"HTML attributes"
)

translations.define("Block.css_class",
    ca = u"Classes CSS",
    es = u"Clases CSS",
    en = u"CSS classes"
)

translations.define("Block.inline_css_styles",
    ca = u"Estils en línia",
    es = u"Estilos en linea",
    en = u"Inline CSS styles"
)

translations.define("Block.enabled",
    ca = u"Actiu",
    es = u"Activo",
    en = u"Active"
)

# ContainerBlock
#------------------------------------------------------------------------------
translations.define("ContainerBlock",
    ca = u"Contenidor",
    es = u"Contenedor",
    en = u"Container"
)

translations.define("ContainerBlock-plural",
    ca = u"Contenidors",
    es = u"Contenedores",
    en = u"Containers"
)

translations.define("ContainerBlock.blocks",
    ca = u"Blocs fills",
    es = u"Bloques hijos",
    en = u"Child blocks"
)

# SlideShowBlock
#------------------------------------------------------------------------------
translations.define("SlideShowBlock",
    ca = u"Passador",
    es = u"Pasador",
    en = u"Slide show"
)

translations.define("SlideShowBlock-plural",
    ca = u"Passadors",
    es = u"Pasadores",
    en = u"Slide shows"
)

translations.define("SlideShowBlock.transition_settings",
    ca = u"Transicions",
    es = u"Transiciones",
    en = u"Transitions"
)

translations.define("SlideShowBlock.autoplay",
    ca = u"Transicions automàtiques",
    es = u"Transiciones automáticas",
    en = u"Autoplay"
)

translations.define("SlideShowBlock.navigation_controls",
    ca = u"Mostrar controls de navegació",
    es = u"Mostrar controles de navegación",
    en = u"Show navigation controls"
)

translations.define("SlideShowBlock.interval",
    ca = u"Freqüència de les transicions",
    es = u"Frecuencia de las transiciones",
    en = u"Time between transitions"
)

translations.define("SlideShowBlock.interval-explanation",
    ca = u"Si s'activen les transicions automàtiques, indica el nombre de "
         u"milisegons abans que el bloc passi a la següent diapositiva.",
    es = u"Si se activan las transiciones automáticas, indica el número de "
         u"milisegundos antes que el bloque pase a la diapositiva siguiente.",
    en = u"If autoplay is enabled, indicates the number of milliseconds that "
         u"pass between automatic transitions."
)

translations.define("SlideShowBlock.transition_duration",
    ca = u"Duració de les transicions",
    es = u"Duración de las transiciones",
    en = u"Transition duration"
)

translations.define("SlideShowBlock.interval-explanation",
    ca = u"Especifica la duració de l'efecte de transició, en milisegons",
    es = u"Especifica la duración del efecto de transición, en milisegundos",
    en = u"Sets the duration of the slide transition effect, in milliseconds"
)

# MenuBlock
#------------------------------------------------------------------------------
translations.define("MenuBlock",
    ca = u"Menú",
    es = u"Menú",
    en = u"Menu"
)

translations.define("MenuBlock-plural",
    ca = u"Menús",
    es = u"Menús",
    en = u"Menus"
)

translations.define("MenuBlock.root",
    ca = u"Arrel",
    es = u"Raiz",
    en = u"Root"
)

translations.define("MenuBlock.root_visible",
    ca = u"Arrel visible",
    es = u"Raiz visible",
    en = u"Root visible"
)

translations.define("MenuBlock.max_depth",
    ca = u"Profunditat màxima",
    es = u"Profundidad máxima",
    en = u"Maximum depth"
)

translations.define("MenuBlock.expanded",
    ca = u"Expandit",
    es = u"Expandido",
    en = u"Expanded"
)

# HTMLBlock
#------------------------------------------------------------------------------
translations.define("HTMLBlock",
    ca = u"HTML",
    es = u"HTML",
    en = u"HTML"
)

translations.define("HTMLBlock-plural",
    ca = u"HTML",
    es = u"HTML",
    en = u"HTML"
)

translations.define("HTMLBlock.html",
    ca = u"HTML",
    es = u"HTML",
    en = u"HTML"
)

# TextBlock
#------------------------------------------------------------------------------
translations.define("TextBlock",
    ca = u"Text + imatges",
    es = u"Texto + imágenes",
    en = u"Text + images"
)

translations.define("TextBlock-plural",
    ca = u"Text + imatges",
    es = u"Texto + imágenes",
    en = u"Text + images"
)

translations.define("TextBlock.link",
    ca = u"Enllaç",
    es = u"Enlace",
    en = u"Link"
)

translations.define("TextBlock.link_destination",
    ca = u"Destí de l'enllaç",
    es = u"Destino del enlace",
    en = u"Linked resource"
)

translations.define("TextBlock.link_opens_in_new_window",
    ca = u"Obrir l'enllaç a una nova finestra",
    es = u"Abrir el enlace en una ventana nueva",
    en = u"Open the link in a new window"
)

translations.define("TextBlock.text",
    ca = u"Text",
    es = u"Texto",
    en = u"Text"
)

translations.define("TextBlock.images",
    ca = u"Imatges",
    es = u"Imágenes",
    en = u"Images"
)

translations.define("TextBlock.image_gallery_type",
    ca = u"Presentació de les imatges",
    es = u"Presentación de las imágenes",
    en = u"Image presentation"
)

translations.define("TextBlock.image_gallery_type=thumbnails",
    ca = u"Miniatures",
    es = u"Miniaturas",
    en = u"Thumbnails"
)

translations.define("TextBlock.image_gallery_type=slideshow",
    ca = u"Passador",
    es = u"Pasador",
    en = u"Slideshow"
)

translations.define("TextBlock.image_alignment",
    ca = u"Disposició de les imatges",
    es = u"Disposición de las imágenes",
    en = u"Image alignment"
)

translations.define("TextBlock.image_alignment=float_top_left",
    ca = u"Flotar a l'esquerra",
    es = u"Flotar a la izquierda",
    en = u"Top left, floating"
)

translations.define("TextBlock.image_alignment=float_top_right",
    ca = u"Flotar a la dreta",
    es = u"Flotar a la derecha",
    en = u"Top right, floating"
)

translations.define("TextBlock.image_alignment=column_left",
    ca = u"Columna a l'esquerra",
    es = u"Columna a la izquierda",
    en = u"Top left, in their own column"
)

translations.define("TextBlock.image_alignment=column_right",
    ca = u"Columna a la dreta",
    es = u"Columna a l'esquerra",
    en = u"Top right, in their own column"
)

translations.define("TextBlock.image_alignment=center_top",
    ca = u"Centrar a dalt",
    es = u"Centrar arriba",
    en = u"Top center"
)

translations.define("TextBlock.image_thumbnail_factory",
    ca = u"Processat de les imatges",
    es = u"Procesado de las imágenes",
    en = u"Image processing"
)

translations.define("TextBlock.image_close_up_enabled",
    ca = u"Ampliar les imatges en fer-hi clic",
    es = u"Ampliar las imágenes al pulsarlas",
    en = u"Click to enlarge"
)

translations.define("TextBlock.image_close_up_factory",
    ca = u"Processat de les imatges ampliades",
    es = u"Procesado de las imágenes ampliadas",
    en = u"Image processing for enlarged images"
)

translations.define("TextBlock.image_close_up_preload",
    ca = u"Precàrrega de les imatges ampliades",
    es = u"Precarga de las imágenes ampliadas",
    en = u"Preload enlarged images"
)

translations.define("TextBlock.image_labels_visible",
    ca = u"Mostrar els títols de les imatges",
    es = u"Mostrar los títulos de las imágenes",
    en = u"Show image titles"
)

translations.define("TextBlock.image_original_link_visible",
    ca = u"Mostrar un enllaç a la imatge sense modificar",
    es = u"Mostrar un enlace a la imagen sin modificar",
    en = u"Show a link to the original image"
)

# VimeoBlock
#------------------------------------------------------------------------------
translations.define("VimeoBlock",
    ca = u"Vídeo de Vimeo",
    es = u"Video de Vimeo",
    en = u"Vimeo video"
)

translations.define("VimeoBlock-plural",
    ca = u"Vídeos de Vimeo",
    es = u"Vídeos de Vimeo",
    en = u"Vimeo videos"
)

translations.define("VimeoBlock.video",
    ca = u"Vídeo",
    es = u"Video",
    en = u"Video"
)

translations.define("VimeoBlock.video_width",
    ca = u"Amplada",
    es = u"Ancho",
    en = u"Width"
)

translations.define("VimeoBlock.video_width-explanation",
    ca = u"en píxels",
    es = u"en píxeles",
    en = u"in pixels"
)

translations.define("VimeoBlock.video_height",
    ca = u"Alçada",
    es = u"Alto",
    en = u"Height"
)

translations.define("VimeoBlock.video_height-explanation",
    ca = u"en píxels",
    es = u"en píxeles",
    en = u"in pixels"
)

# TwitterTimelineBlock
#------------------------------------------------------------------------------
translations.define("TwitterTimelineBlock",
    ca = u"Missatges de Twitter",
    es = u"Mensajes de Twitter",
    en = u"Twitter timeline"
)

translations.define("TwitterTimelineBlock-plural",
    ca = u"Missatges de Twitter",
    es = u"Mensajes de Twitter",
    en = u"Twitter timeline"
)

translations.define("TwitterTimelineBlock.account",
    ca = u"Compte de Twitter",
    es = u"Cuenta de Twitter",
    en = u"Twitter account"
)

translations.define("TwitterTimelineBlock.max_tweets",
    ca = u"Missatges a mostrar",
    es = u"Mensajes a mostrar",
    en = u"Max tweets"
)

# LinksBox
#------------------------------------------------------------------------------
translations.define("LinksBlock",
    ca = u"Llista d'enllaços",
    es = u"Lista de enlaces",
    en = u"Link list"
)

translations.define("LinksBlock-plural",
    ca = u"Llistes d'enllaços",
    es = u"Listas de enlaces",
    en = u"Link lists"
)

translations.define("LinksBlock.links",
    ca = u"Enllaços",
    es = u"Enlaces",
    en = u"Links"
)

# FolderBlock
#------------------------------------------------------------------------------
translations.define("FolderBlock",
    ca = u"Llistat de documents fills",
    es = u"Listado de documentos hijos",
    en = u"Child documents listing"
)

translations.define("FolderBlock-plural",
    ca = u"Llistats de documents fills",
    es = u"Listados de documentos hijos",
    en = u"Child documents listings"
)

translations.define("FolderBlock.show_hidden_children",
    ca = u"Mostrar documents ocults",
    es = u"Mostrar documentos ocultos",
    en = u"Show hidden documents"
)

translations.define("FolderBlock.show_thumbnails",
    ca = u"Mostrar miniatures",
    es = u"Mostrar miniaturas",
    en = u"Show thumbnails"
)

translations.define("FolderBlock.thumbnails_factory",
    ca = u"Processador de miniatures",
    es = u"Procesador de miniaturas",
    en = u"Thumbnail factory"
)

# LoginBlock
#------------------------------------------------------------------------------
translations.define("LoginBlock",
    ca = u"Formulari d'autenticació d'usuari",
    es = u"Formulario de autenticación de usuario",
    en = u"Login form"
)

translations.define("LoginBlock-plural",
    ca = u"Formularis d'autenticació d'usuari",
    es = u"Formularios de autenticación de usuario",
    en = u"Login forms"
)

translations.define("LoginBlock.login_target",
    ca = u"Pàgina de destí",
    es = u"Página de destino",
    en = u"Destination page"
)

translations.define("LoginBlock.login_target-explanation",
    ca = u"La pàgina que rebrà la petició d'autenticació de l'usuari",
    es = u"La pàgina que recibirá la petición de autenticación del "
         u"usuario",
    en = u"The page that will handle the user's authentication request"
)

translations.define("LoginBlockForm.user",
    ca = u"Usuari",
    es = u"Usuario",
    en = u"User"
)

translations.define("LoginBlockForm.password",
    ca = u"Contrasenya",
    es = u"Contraseña",
    en = u"Password"
)

translations.define("woost.extensions.blocks.LoginBlockView.submit_button",
    ca = u"Entrar",
    es = u"Entrar",
    en = u"Login"
)

# IFrameBlock
#------------------------------------------------------------------------------
translations.define("IFrameBlock",
    ca = u"IFrame",
    es = u"IFrame",
    en = u"IFrame"
)

translations.define("IFrameBlock-plural",
    ca = u"IFrames",
    es = u"IFrames",
    en = u"IFrames"
)

translations.define("IFrameBlock.src",
    ca = u"Adreça a mostrar",
    es = u"Dirección a mostrar",
    en = u"Content URL"
)

translations.define("IFrameBlock.width",
    ca = u"Amplada",
    es = u"Ancho",
    en = u"Width"
)

translations.define("IFrameBlock.height",
    ca = u"Alçada",
    es = u"Alto",
    en = u"Height"
)

# EditBlocksView
#------------------------------------------------------------------------------
translations.define("woost.extensions.blocks.EditBlocksView.body_header",
    ca = lambda item: 
        u"Editant els blocs " + ca_possessive(translations(item)),
    es = lambda item:
        u"Editando los bloques de " + translations(item),
    en = lambda item:
        u"Editing the blocks for " + translations(item)
)

# EditBlocksSlotList
#------------------------------------------------------------------------------
translations.define(
    "woost.extensions.blocks.EditBlocksSlotList.new_blocks_panel.panel_header",
    ca = u"Nou bloc",
    es = u"Nuevo bloque",
    en = u"New block"
)

translations.define(     
    "woost.extensions.blocks.EditBlocksSlotList.common_blocks_panel.panel_header",
    ca = u"Blocs comuns",
    es = u"Bloques comunes",
    en = u"Common blocks"
)

translations.define(
    "woost.extensions.blocks.EditBlocksSlotList.dialog_buttons.cancel_button",
    ca = u"Cancel·lar",
    es = u"Cancelar",
    en = u"Cancel"
)

# BlockDisplay
#------------------------------------------------------------------------------
translations.define("woost.extensions.blocks.BlockDisplay.common_status.label",
    ca = u"Comú",
    es = u"Común",
    en = u"Common"
)

translations.define("woost.extensions.blocks.BlockDisplay.common_status.title",
    ca = u"Aquest bloc resideix a la llibreria de blocs comuns, i pot "
         u"aparèixer a més d'una pàgina",
    es = u"Este bloque reside en la libreria de bloques comunes, pudiendo "
         u"aparecer en más de una página",
    en = u"This block resides within the site's common blocks gallery, and "
         u"it may appear in more than one page"
)

translations.define("woost.extensions.blocks.BlockDisplay.disabled_status.label",
    ca = u"Inactiu",
    es = u"Inactivo",
    en = u"Disabled"
)

translations.define("woost.extensions.blocks.BlockDisplay.disabled_status.title",
    ca = u"Aquest bloc està deshabilitat, no s'inclourà a la pàgina",
    es = u"Este bloque está deshabilitado, no se incluirá en la página",
    en = u"This block is disabled and won't be displayed in the page"
)

translations.define("Action add_block",
    ca = u"Afegir",
    es = u"Añadir",
    en = u"Add"
)

translations.define("Action add_block_before",
    ca = u"Afegir davant",
    es = u"Añadir en frente",
    en = u"Add before"
)

translations.define("Action add_block_after",
    ca = u"Afegir darrere",
    es = u"Añadir detrás",
    en = u"Add after"
)

translations.define("Action edit_block",
    ca = u"Editar",
    es = u"Editar",
    en = u"Edit"
)

translations.define("Action remove_block",
    ca = u"Treure",
    es = u"Quitar",
    en = u"Remove"
)

translations.define("Action cut_block",
    ca = u"Retallar",
    es = u"Cortar",
    en = u"Cut"
)

translations.define("Action paste_block",
    ca = u"Enganxar",
    es = u"Pegar",
    en = u"Paste"
)

translations.define("Action paste_block_after",
    ca = u"Enganxar darrere",
    es = u"Pegar detrás",
    en = u"Paste after"
)

translations.define("Action paste_block_before",
    ca = u"Enganxar davant",
    es = u"Pegar delante",
    en = u"Paste before"
)

translations.define("Action share_block",
    ca = u"Afegir a la llibreria",
    es = u"Añadir a la libreria",
    en = u"Add to the library"
)

translations.define("woost.extensions.blocks.empty_clipboard",
    ca = u"El portaretalls no conté cap bloc",
    es = u"El portapapeles no cotiene ningún bloque",
    en = u"The clipboard is empty"
)

translations.define("woost.extensions.blocks.clipboard_error",
    ca = u"El contingut del portaretalls no és vàlid",
    es = u"El contenido del portapapeles no es válido",
    en = u"The clipboard content is not valid"
)

