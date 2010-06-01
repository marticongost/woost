#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""
from os.path import abspath, dirname, join
from cocktail.html import templates, Element
from cocktail.translations import translations
from cocktail.controllers import context
from woost.models import Style

TinyMCE = templates.get_class("cocktail.html.TinyMCE")

#Required Version: 3.2.2.3 TinyMCE
class RichTextEditor(TinyMCE):

    default_tinymce_params = {
        "plugins": "fullscreen, paste, inlinepopups, advimage, contextmenu, -advimagescale",
        "entity_encoding": "raw",
        "dialog_type": "modal",
        "theme": "advanced",
        "theme_advanced_buttons1_add": "fullscreen",
        "theme_advanced_buttons2_add": "pastetext,pasteword,selectall",
        "theme_advanced_buttons3": "",
        "theme_advanced_toolbar_location": "top",
        "theme_advanced_resizing": True,
        "theme_advanced_statusbar_location": "bottom",
        "theme_advanced_toolbar_align": "left",
        "theme_advanced_path": False,
        "theme_advanced_resize_horizontal": False,
        "document_base_url": "/",
        "relative_urls": False,
        "content_css": "/user_styles/?backoffice=1",
        "fullscreen_settings": {
            "theme_advanced_toolbar_location": "top"
        }
    }

    def _ready(self):

        ctx_uri = context["cms"].contextual_uri()
        current_edit_stack = \
            context["edit_stacks_manager"].current_edit_stack
        
        styles = [
            "%s=%s" % (translations(style), style.class_name)
            for style in Style.select()
        ]

        self.tinymce_params.update(self.default_tinymce_params)

        if current_edit_stack:
            edit_stack_param = current_edit_stack.to_param()
            self.tinymce_params.update(
                init_instance_callback = "initRichTextEditor",
                theme_advanced_styles = ";".join(styles),
                external_image_list_url = "%s/editor_attachments?edit_stack=%s&resource_type=image&language=%s"
                    % (ctx_uri, edit_stack_param, self.language),
                external_link_list_url = "%s/editor_attachments?edit_stack=%s&resource_type=document&language=%s"
                    % (ctx_uri, edit_stack_param, self.language),
                media_external_list_url = "%s/editor_attachments?edit_stack=%s&resource_type=video&language=%s"
                    % (ctx_uri, edit_stack_param, self.language),
            )
        

        load_plugin = Element("script")
        load_plugin["type"] = "text/javascript"
        load_plugin.append("tinymce.PluginManager.load('advimagescale', '/resources/scripts/advimagescale/editor_plugin.js');")
        self.append(load_plugin)
        
        TinyMCE._ready(self)
        
    def __init__(self, *args, **kwargs):
        TinyMCE.__init__(self, *args, **kwargs)
        self.add_resource("/resources/scripts/RichTextEditor.js")

