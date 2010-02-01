#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from cocktail.modeling import getter
from cocktail.events import event_handler
from cocktail import schema
from woost.models.publishable import Publishable
from woost.models.controller import Controller


class Document(Publishable):

    instantiable = True
    default_per_language_publication = True

    groups_order = ["content"]

    members_order = (
        "title",
        "inner_title",        
        "template",
        "description",
        "keywords",
        "attachments",
        "page_resources",
        "branch_resources",
        "children"
    )

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(qname = "woost.document_controller")
    )

    title = schema.String(
        indexed = True,
        normalized_index = True,
        translated = True,
        required = True,
        member_group = "content"
    )

    inner_title = schema.String(
        translated = True,
        listed_by_default = False,
        member_group = "content"
    )

    description = schema.String(
        translated = True,
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea",
        member_group = "content"
    )

    keywords = schema.String(
        translated = True,
        listed_by_default = False,
        edit_control = "cocktail.html.TextArea",
        member_group = "content"
    )

    template = schema.Reference(
        type = "woost.models.Template",
        bidirectional = True,
        listed_by_default = False,
        member_group = "presentation"
    )

    branch_resources = schema.Collection(
        items = schema.Reference(
            type = Publishable,
            required = True,
            relation_constraints =
                Publishable.resource_type.equal("html_resource")
        ),
        related_end = schema.Collection()
    )

    page_resources = schema.Collection(
        items = schema.Reference(
            type = Publishable,
            required = True,
            relation_constraints =
                Publishable.resource_type.equal("html_resource")
        ),
        related_end = schema.Collection()
    )

    attachments = schema.Collection(
        items = schema.Reference(
            type = Publishable,
            required = True
        ),
        related_end = schema.Collection()
    )
 
    children = schema.Collection(
        items = "woost.models.Publishable",
        bidirectional = True,
        related_key = "parent",
        cascade_delete = True
    )
 
    def __translate__(self, language, **kwargs):
        return (self.draft_source is None and self.get("title", language)) \
            or Publishable.__translate__(self, language, **kwargs)

    def _update_path(self, parent, path):

        Publishable._update_path(self, parent, path)

        if self.children:
            for child in self.children:
                child._update_path(self, child.path)

    def descend_tree(self, include_self = False):

        if include_self:
            yield self

        if self.children:
            for child in self.children:
                for descendant in child.descend_tree(True):
                    yield descendant

    @getter
    def resources(self):
        """Iterates over all the resources that apply to the page.
        @type: L{Publishable}
        """
        ancestry = list(self.ascend_tree(include_self = True))
        ancestry.reverse()

        for page in ancestry:
            for resource in page.branch_resources:
                yield resource

        for resource in self.page_resources:
            yield resource

