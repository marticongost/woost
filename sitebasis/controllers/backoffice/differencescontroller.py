#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			November 2008
"""
from cocktail.modeling import cached_getter
from cocktail.schema import Collection, String, DictAccessor
from sitebasis.controllers.backoffice.editcontroller import EditController
from sitebasis.controllers.backoffice.useractions import get_user_action


class DifferencesController(EditController):

    view_class = "sitebasis.views.BackOfficeDiffView"
    section = "diff"

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
        
        self.context["parent_handler"].switch_section("fields")

    @cached_getter
    def output(self):
        output = EditController.output(self)
        output.update(
            submitted = False,
            source = self.stack_node.item,
            target = self.stack_node.form_data,
            selected_action = get_user_action("diff")
        )
        return output

