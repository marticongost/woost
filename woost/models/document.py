"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema
from cocktail.events import event_handler
from cocktail.controllers import redirect

from .publishable import Publishable
from .theme import Theme
from .style import Style
from .metatags import MetaTags
from .seometadata import seo_metadata


@seo_metadata
class Document(Publishable):

    instantiable = False
    type_group = "document"
    admin_show_descriptions = False
    default_per_language_publication = True

    groups_order = list(Publishable.groups_order) + [
        "meta",
        "robots"
    ]

    members_order = (
        "title",
        "inner_title",
        "summary",
        "template",
        "theme",
        "styles",
        "children"
    )

    title = schema.String(
        indexed=True,
        normalized_index=True,
        full_text_indexed=True,
        descriptive=True,
        translated=True,
        required=True,
        spellcheck=True,
        member_group="content"
    )

    inner_title = schema.HTML(
        translated=True,
        tinymce_params={
            "forced_root_block": "",
            "force_p_newlines": False,
            "height": "70px"
        },
        listed_by_default=False,
        ui_form_control=(
            "cocktail.ui.HTMLEditor",
            {"inlineContent": True}
        ),
        member_group="content"
    )

    summary = schema.HTML(
        translated=True,
        spellcheck=True,
        listed_by_default=False,
        member_group="content"
    )

    meta_tags = MetaTags(
        member_group="meta"
    )

    template = schema.Reference(
        type="woost.models.Template",
        bidirectional=True,
        listed_by_default=False,
        after_member="controller",
        shadows_attribute=True,
        member_group="presentation.behavior"
    )

    theme = schema.Reference(
        type=Theme,
        related_end=schema.Collection(),
        listed_by_default=False,
        member_group="presentation.behavior",
        shadows_attribute=True
    )

    styles = schema.Collection(
        items=schema.Reference(type=Style),
        related_end=schema.Collection(),
        relation_constraints={"applicable_to_documents": True},
        after_member="template",
        member_group="presentation.behavior"
    )

    children = schema.Collection(
        items="woost.models.Publishable",
        bidirectional=True,
        related_key="parent",
        cascade_delete=True,
        after_member="parent",
        member_group="navigation"
    )

    def _update_path(self, parent, path):

        Publishable._update_path(self, parent, path)

        if self.children:
            for child in self.children:
                child._update_path(self, child.path)

    def descend_tree(self, include_self=False):

        if include_self:
            yield self

        if self.children:
            for child in self.children:
                for descendant in child.descend_tree(True):
                    yield descendant

    def render(self, **values):
        """Renders the document using its template."""

        template = self.get_template()

        if template is None:
            raise ValueError("Can't render a document without a template")

        values["publishable"] = self

        view = template.create_view()
        for key, value in values.items():
            setattr(view, key, value)

        html = view.render_page()
        view.dispose()
        return html

    def find_first_child_redirection_target(self):
        for child in self.children:
            if child.is_accessible():
                if isinstance(child, Document):
                    return child.find_redirection_target() or child
                else:
                    return child

    def first_child_redirection(self):
        child = self.find_first_child_redirection_target()
        if child is not None:
            redirect(child.get_uri())

    @event_handler
    def handle_related(event):
        if event.member is Document.websites:
            for child in event.source.children:
                child.websites = set(event.source.websites)

    @event_handler
    def handle_unrelated(event):
        if not event.source.is_deleted:
            if event.member is Document.websites:
                for child in event.source.children:
                    child.websites = set(event.source.websites)

