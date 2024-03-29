#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from cocktail.html import templates, Element
from cocktail.translations import translations
from woost.models import Style

TinyMCE = templates.get_class("cocktail.html.TinyMCE")


class RichTextEditor(TinyMCE):

    # Required TinyMCE version: 3.2.2.3

    tinymce_params = {
        "plugins": "fullscreen, paste, media, inlinepopups, advimage, "
                   "contextmenu, tabfocus, -advimagescale",
        "entity_encoding": "raw",
        "dialog_type": "modal",
        "theme": "advanced",
        "theme_advanced_buttons1_add": "removeformat",
        "theme_advanced_buttons2_add": "selectall, | , fullscreen",
        "theme_advanced_buttons3": "",
        "theme_advanced_toolbar_location": "top",
        "theme_advanced_resizing": True,
        "theme_advanced_statusbar_location": "bottom",
        "theme_advanced_toolbar_align": "left",
        "theme_advanced_path": False,
        "theme_advanced_resize_horizontal": False,
        "theme_advanced_blockformats": "p,h1,h2,h3,h4,h5,h6,pre,address,blockquote",
        "document_base_url": "/",
        "relative_urls": False,
        "content_css": "/user_styles/?backoffice=1",
        "fullscreen_settings": {
            "theme_advanced_toolbar_location": "top"
        },
        "height": 250,
        "media_strict": False,
        "paste_text_sticky_default": True
    }

    def _ready(self):

        styles = [
            "%s=%s" % (translations(style), style.class_name)
            for style in Style.select({"applicable_to_text": True})
        ]

        d = self.tinymce_params.setdefault
        d("theme_advanced_styles", ";".join(styles))
        d("init_instance_callback", "woost.initRichTextEditor")

        load_plugin = Element("script")
        load_plugin["type"] = "text/javascript"
        load_plugin.append("tinymce.PluginManager.load('advimagescale', '/resources/scripts/advimagescale/editor_plugin.js');")
        self.append(load_plugin)

        TinyMCE._ready(self)

    def __init__(self, *args, **kwargs):
        TinyMCE.__init__(self, *args, **kwargs)
        self.add_resource("/resources/scripts/RichTextEditor.js")

