#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Jordi Fernández <jordi.fernandez@whads.com>
"""
from cocktail.translations import translations
from cocktail import schema
from cocktail.html import templates
from woost.models import Extension, Site


translations.define("BlocksExtension",
    ca = u"Blocs de contingut",
    es = u"Bloques de contenido",
    en = u"Content blocks"
)

translations.define("BlocksExtension-plural",
    ca = u"Blocs de contingut",
    es = u"Bloques de contenido",
    en = u"Content blocks"
)


class BlocksExtension(Extension):

    unusable_image_factories = (
        "icon16",
        "icon32",
        "backoffice_thumbnail",
        "backoffice_small_thumbnail"
    )

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Permet la creació de contingut utilitzant blocs""",
            "ca"
        )
        self.set("description",            
            u"""Permite la creación de contenido usando bloques""",
            "es"
        )
        self.set("description",
            u"""Allows the creation of content using blocs""",
            "en"
        )

    def _load(self):

        from woost.extensions.blocks.block import Block
        from woost.extensions.blocks import (
            strings,
            customblock,
            containerblock,
            slideshowblock,
            menublock,
            htmlblock,
            textblock,
            twittertimelineblock,
            loginblock,
            iframeblock,
            youtubeblock,
            newslisting,
            filelisting,
            blockspage,
            blockactions,
            site,
            news,
            imagefactory,
            utils,
            migration
        )

        from woost.extensions.vimeo import VimeoExtension

        if VimeoExtension.instance.enabled:
            from woost.extensions.blocks import vimeoblock

        # Install an overlay for the frontend edit panel
        templates.get_class("woost.extensions.blocks.EditPanelOverlay")

        # Add a module to the backoffice for editing block hierarchies
        # in a more visual fashion
        from woost.controllers.backoffice.backofficecontroller \
            import BackOfficeController
        from woost.extensions.blocks.editblockscontroller \
            import EditBlocksController
        BackOfficeController.blocks = EditBlocksController

        from woost.extensions.blocks.dropblockcontroller \
            import DropBlockController
        BackOfficeController.drop_block = DropBlockController

        # Remove all relations to blocks from the edit view
        from woost.controllers.backoffice.editstack import EditNode
        base_should_exclude_member = EditNode.should_exclude_member

        def should_exclude_member(self, member):
            return base_should_exclude_member(self, member) or (
                isinstance(member, schema.RelationMember)
                and member.related_type
                and issubclass(member.related_type, Block)
            )

        EditNode.should_exclude_member = should_exclude_member

        self.install()

    def _install(self):
        from woost.models import Template, extension_translations

        self._create_asset(
            Template,
            "blocks_page_template",
            title = extension_translations,
            engine = "cocktail",
            identifier = "woost.extensions.blocks.BlocksPageView"
        )

        self._create_image_factories()

    def _create_image_factories(self):
        from woost.models import extension_translations
        from woost.models.rendering import ImageFactory, Thumbnail, Frame
         
        for factory_id in self.unusable_image_factories:
            factory = ImageFactory.get_instance(identifier = factory_id)
            if factory is not None:
                factory.applicable_to_blocks = False

        ImageFactory.applicable_to_blocks.rebuild_index()

        edit_blocks_thumbnail = self._create_asset(
            ImageFactory,
            "edit_blocks_thumbnail_image_factory",
            title = extension_translations,
            identifier = "edit_blocks_thumbnail",
            effects = [
                Thumbnail(width = "75", height = "75"),
                Frame(
                    edge_width = 1,
                    edge_color = "ccc",
                    vertical_padding = "4",
                    horizontal_padding = "4",
                    background = "eee"
                )
            ]
        )

        Site.main.image_factories.append(edit_blocks_thumbnail)

