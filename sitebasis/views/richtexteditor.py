#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from os.path import abspath, dirname, join
from cocktail.html import templates
from cocktail.translations import translations
from cocktail.controllers import context
from sitebasis.models import Style

TinyMCE = templates.get_class("cocktail.html.TinyMCE")

#Required Version: 3.2.2.3 TinyMCE
class RichTextEditor(TinyMCE):
    
    

    def __init__(self, *args, **kwargs):
        TinyMCE.__init__(self, *args, **kwargs)
        self.add_resource("/resources/scripts/RichTextEditor.js")                        

        styles = [
            "%s=%s" % (translations(style), style.class_name)
            for style in Style.select()
        ]

        self.tinymce_params.update(
            init_instance_callback = "initRichTextEditor",
            plugins = "fullscreen, paste, inlinepopups, advimage",
            entity_encoding = "raw",
            theme = "advanced",
            dialog_type = "modal",            
            theme_advanced_buttons1_add = "fullscreen",
            theme_advanced_buttons2_add = "pastetext,pasteword,selectall",
            theme_advanced_buttons3 = "",
            theme_advanced_toolbar_location = "top",
            theme_advanced_resizing = True,
            theme_advanced_statusbar_location = "bottom",
            theme_advanced_toolbar_align = "left",
            theme_advanced_path = False,
            theme_advanced_resize_horizontal = False,
            external_image_list_url = "/cms/document_images?edit_stack=%s" % \
                    (context["edit_stacks_manager"].current_edit_stack.to_param()),
            external_link_list_url = "/cms/document_files?edit_stack=%s" % \
                    (context["edit_stacks_manager"].current_edit_stack.to_param()),
            theme_advanced_styles = ";".join(styles),
            document_base_url = "/",
            relative_urls = False,
            content_css = "/user_styles/",
#            fullscreen_new_window = True
            fullscreen_settings = {
                "theme_advanced_toolbar_location": "bottom"
            }
        )
