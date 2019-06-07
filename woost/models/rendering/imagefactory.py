#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from collections import defaultdict
import piexif
from PIL import Image
from cocktail.events import event_handler
from cocktail.iteration import first
from cocktail import schema
from woost.models.item import Item
from woost.models.rendering.renderer import Renderer


class ImageFactory(Item):

    visible_from_root = False

    members_order = [
        "title",
        "identifier",
        "renderer",
        "default_format",
        "effects",
        "options_code",
        "fallback",
        "applicable_to_blocks"
    ]

    preserved_exif_fields = [
        "0th.269", # DocumentName
        "1st.269", # DocumentName
        "0th.270", # ImageDescription
        "1st.270", # ImageDescription
        "0th.315", # Artist
        "1st.315", # Artist
        "0th.33432", # Copyright
        "1st.33432", # Copyright
        "Exif.37510" # UserComment
    ]

    title = schema.String(
        translated = True,
        descriptive = True
    )

    identifier = schema.String(
        unique = True,
        indexed = True,
        normalized_index = False
    )

    renderer = schema.Reference(
        required = True,
        type = Renderer,
        related_end = schema.Collection(),
        default = schema.DynamicDefault(
            lambda: Item.get_instance(qname = "woost.content_renderer")
        ),
        edit_control = "cocktail.html.DropdownSelector"
    )

    default_format = schema.String(
        enumeration = ["JPEG", "PNG", "GIF"],
        translatable_enumeration = False,
        edit_control = "cocktail.html.DropdownSelector"
    )

    effects = schema.Collection(
        items = "woost.models.rendering.ImageEffect",
        bidirectional = True,
        integral = True,
    )

    options_code = schema.CodeBlock(
        language = "python"
    )

    fallback = schema.Reference(
        type = "woost.models.rendering.ImageFactory",
        bidirectional = True
    )

    fallback_referers = schema.Collection(
        items = "woost.models.rendering.ImageFactory",
        bidirectional = True,
        visible = False
    )

    applicable_to_blocks = schema.Boolean(
        required = True,
        default = True,
        indexed = True
    )

    def render(self, item):

        image = self.renderer.render(item)

        if image is None:
            if self.fallback:
                image = self.fallback.render(item)
        else:
            if self.effects:
                if isinstance(image, str):
                    image = Image.open(image)

                metadata = self.get_exif_metadata(image)

                for effect in self.effects:
                    image = effect.apply(image)

                if metadata:
                    image.info['exif'] = piexif.dump(metadata)

        return image

    def get_exif_metadata(self, image):

        if "exif" not in image.info:
            return None

        exif_metadata = piexif.load(image.info['exif'])
        new_metadata = defaultdict(dict)

        for exif_field in self.preserved_exif_fields:
            ifd, field_code = exif_field.split(".")
            field_code = int(field_code)
            original_value = exif_metadata[ifd].get(field_code)

            if original_value:
                new_metadata[ifd][field_code] = original_value

        return new_metadata

    def can_render(self, item, resolve_representative = True, **parameters):
        """Indicates if the renderers used by the image factory are able to
        render the given item.

        @param item: The item to evaluate.
        @type item: L{Item<woost.models.item.Item>}

        @return: True if the image factory claims to be able to render the
            item, False otherwise.
        @rtype: bool
        """
        if resolve_representative:
            item = item.resolve_representative_image(self)
        return (
            self.renderer.can_render(item, **parameters)
            or self.fallback and self.fallback.can_render(item, **parameters)
        )

    cache_invalidators = frozenset((
        identifier,
        renderer,
        effects,
        fallback
    ))

    @event_handler
    def handle_changing(e):
        from woost.models.rendering.request \
            import clear_image_cache_after_commit
        if e.source.is_inserted and e.member in ImageFactory.cache_invalidators:
            clear_image_cache_after_commit(factory = e.source)
            for referer in e.source.fallback_referers:
                clear_image_cache_after_commit(factory = referer)

    @event_handler
    def handle_related(e):
        from woost.models.rendering.request \
            import clear_image_cache_after_commit
        if e.source.is_inserted and e.member in ImageFactory.cache_invalidators:
            clear_image_cache_after_commit(factory = e.source)
            for referer in e.source.fallback_referers:
                clear_image_cache_after_commit(factory = referer)

    @event_handler
    def handle_unrelated(e):
        from woost.models.rendering.request \
            import clear_image_cache_after_commit
        if e.source.is_inserted and e.member in ImageFactory.cache_invalidators:
            clear_image_cache_after_commit(factory = e.source)
            for referer in e.source.fallback_referers:
                clear_image_cache_after_commit(factory = referer)

    @event_handler
    def handle_deleting(e):
        from woost.models.rendering.request \
            import clear_image_cache_after_commit
        clear_image_cache_after_commit(factory = e.source)
        for referer in e.source.fallback_referers:
            clear_image_cache_after_commit(factory = referer)

