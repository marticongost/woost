#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from os.path import abspath, dirname, join
from cocktail.html import templates
from cocktail.translations import translate
from sitebasis.models import Style

TinyMCE = templates.get_class("cocktail.html.TinyMCE")


class RichTextEditor(TinyMCE):
    
    

    def __init__(self, *args, **kwargs):
        TinyMCE.__init__(self, *args, **kwargs)
        self.add_resource("/resources/scripts/RichTextEditor.js")                        

        styles = [
            "%s=%s" % (translate(style), style.class_name)
            for style in Style.select()
        ]

        self.tinymce_params.update(
            init_instance_callback = "initRichTextEditor",
            plugins = "fullscreen, paste",
            entity_encoding = "raw",
            theme = "advanced",
            theme_advanced_buttons1_add = "fullscreen",
            theme_advanced_buttons2_add = "pastetext,pasteword,selectall",
            theme_advanced_buttons3 = "",
            theme_advanced_toolbar_location = "top",
            theme_advanced_resizing = True,
            theme_advanced_statusbar_location = "bottom",
            theme_advanced_toolbar_align = "left",
            theme_advanced_path = False,
            theme_advanced_resize_horizontal = False,
            theme_advanced_styles = ";".join(styles),
            content_css = "/user_styles/",
#            fullscreen_new_window = True
            fullscreen_settings = {
                "theme_advanced_toolbar_location": "bottom"
            }
        )
