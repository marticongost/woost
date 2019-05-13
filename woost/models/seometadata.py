#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema


class SEOMetadata(schema.SchemaObject):

    members_order = [
        "custom_document_title",
        "meta_description",
        "keywords",
        "robots_should_follow"
    ]

    custom_document_title = schema.String(
        translated=True,
        spellcheck=True,
        listed_by_default = False,
        member_group = "meta"
    )

    meta_description = schema.String(
        translated=True,
        spellcheck=True,
        edit_control="cocktail.html.TextArea",
        listed_by_default = False,
        member_group = "meta"
    )

    keywords = schema.String(
        translated = True,
        spellcheck = True,
        edit_control = "cocktail.html.TextArea",
        listed_by_default = False,
        member_group = "meta"
    )

    robots_should_follow = schema.Boolean(
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "meta.robots",
    )


def seo_metadata(cls):
    """A class decorator that adds the members required to customize SEO
    aspects of a publishable object.
    """
    for member in SEOMetadata.ordered_members():
        if member is SEOMetadata.translations or cls.get_member(member.name):
            continue
        cls.add_member(member.copy(), append=True)

    return cls

