#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from cocktail.translations import translations
from cocktail.html import Element

xml_doctype_regex = re.compile(r"<!DOCTYPE .*?>")
xml_pi_regex = re.compile(r"<\?.*?\?>")
xml_comment_regex = re.compile(r"<!--.*?-->")


class Image(Element):

    tag = "img"
    image = None
    image_factory = "default"
    host = None
    styled_class = False
    accessible_check = False
    svg_inclusion = "inline"

    # Make the class usable as a control
    def _get_value(self):
        return self.image

    def _set_value(self, value):
        self.image = value

    value = property(_get_value, _set_value)

    def _ready(self):

        if self.image is None \
        or (self.accessible_check and not self.image.is_accessible()):
            self.visible = False
        else:
            self.depends_on(self.image)
            self["alt"] = translations(
                self.image, discard_generic_translation = True
            )

            file_ext = getattr(self.image, "file_extension", None)

            if file_ext in (".svg", ".svgz"):

                inclusion = self.svg_inclusion

                if inclusion == "inline":
                    self.tag = "div"
                    self.append(self.get_inline_svg())
                else:
                    uri = self.image.get_uri(
                        host = self.host
                    )
                    if inclusion == "object":
                        self.tag = "object"
                        self["type"] = "image/svg+xml"
                        self["data"] = uri
                    elif inclusion == "img":
                        self["src"] = uri
            else:
                self["src"] = self.image.get_image_uri(
                    image_factory = self.image_factory or "default",
                    host = self.host
                )

    def get_inline_svg(self):
        svg_path = self.image.file_path
        with open(svg_path) as file:
            svg = file.read()
            svg = svg.replace("\r\n", "\n")
            svg = xml_pi_regex.sub("", svg)
            svg = xml_doctype_regex.sub("", svg)
            svg = xml_comment_regex.sub("", svg)
            svg = svg.replace("\n\n", "\n").strip()
            return svg

