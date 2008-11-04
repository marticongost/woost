#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from cocktail.schema import Collection, String, DictAccessor
from sitebasis.controllers.backoffice.itemsectioncontroller \
    import ItemSectionController


class DifferencesController(ItemSectionController):

    view_class = "sitebasis.views.BackOfficeDiffView"

    def is_ready(self):
        return self.action is not None

    def submit(self):        
        if self.action == "revert":
            self._revert()

    def _revert(self):

        reverted_members = self.params.read(
            Collection("reverted_members", type = set, items = String))

        form_data = self.form_data
        form_schema = self.form_schema
        source = self.differences_source
        languages = self.translations

        for member in form_schema.members().itervalues():
         
            if isinstance(member, Collection):
                continue
             
            if member.translated:
                for language in languages:
                    if (member.name + "-" + language) in reverted_members:
                        DictAccessor.set(
                            form_data,
                            member.name,
                            source.get(member.name, language),
                            language = language
                        )
            elif member.name in reverted_members:
                DictAccessor.set(
                    form_data,
                    member.name,
                    source.get(member.name)
                )
        
        self.parent.switch_section("fields")

    def _init_view(self, view):
        
        ItemSectionController._init_view(self, view)

        view.edit_state = self.edit_state
        view.edited_item = self.item
        view.edited_content_type = self.edited_content_type
        view.submitted = False
        view.form_errors = self.form_errors
        view.form_schema = self.form_schema
        view.form_data = self.form_data
        view.source = self.differences_source
        view.target = self.form_data
        view.differences = self.differences
        view.translations = self.translations

