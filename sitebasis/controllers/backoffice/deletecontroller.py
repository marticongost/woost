#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			February 2009
"""
from __future__ import with_statement
from ZODB.POSException import ConflictError
from cocktail.modeling import getter, cached_getter, InstrumentedSet
from cocktail.schema import String, Collection, Reference, RelationMember
from cocktail.persistence import datastore, PersistentClass
from sitebasis.models import changeset_context
from sitebasis.controllers.backoffice.basebackofficecontroller \
    import BaseBackOfficeController


class DeleteController(BaseBackOfficeController):
    
    MAX_TRANSACTION_ATTEMPTS = 3

    _delete_dry_run_done = False

    def __init__(self, *args, **kwargs):
        BaseBackOfficeController.__init__(self, *args, **kwargs)

        self._delete_tree = []
        self._blocking_members = []

    @cached_getter
    def selection(self):
        """The selected subset of items that should be deleted.
        @type: L{Item<sitebasis.models.item.Item>} collection
        """
        return self.params.read(
            Collection("selection", items = "sitebasis.models.Item"))

    def _delete_dry_run(self):

        if self._delete_dry_run_done:
            return

        visited = set()

        def recurse(item, container):

            if item in visited:
                return

            visited.add(item)
            deleted_descendants = list()
            container.append((item, deleted_descendants))
            
            for member in item.__class__.members().itervalues():

                if isinstance(member, RelationMember) \
                and member.related_type \
                and isinstance(member.related_type, PersistentClass):
                    
                    if member.block_delete:
                        self._blocking_members.append((item, member))

                    if member.cascade_delete:
                        value = item.get(member)

                        if value is not None:
                            if isinstance(member, Reference):
                                value = (member,)

                            member_container = list()
                            for descendant in value:
                                if descendant is not None:
                                    recurse(descendant, member_container)
       
                            if len(member_container) > 0:
                                deleted_descendants.append(
                                    (member, member_container)
                                )

        for item in self.selection:
            recurse(item, self._delete_tree)
        
        self._delete_dry_run_done = True

    @getter
    def delete_tree(self):
        self._delete_dry_run()
        return self._delete_tree

    @getter
    def blocking_members(self):
        self._delete_dry_run()
        return self._blocking_members

    @cached_getter
    def action(self):
        """A string identifier indicating the action that has been activated by
        the user.
        @type: str or None
        """
        return self.params.read(String("action"))

    @cached_getter
    def submitted(self):
        return self.action is not None
    
    def submit(self):
        if self.action == "confirm_delete":

            restrict_access = self.restrict_access

            class ValidatingDeletedSet(InstrumentedSet):
                def item_added(self, item):
                    restrict_access(
                        action = "delete",
                        target_instance = item
                    )
            
            user = self.user
            
            for i in range(self.MAX_TRANSACTION_ATTEMPTS):
                deleted_set = ValidatingDeletedSet()

                with changeset_context(author = user):
                    for item in self.selection:
                        item.delete(deleted_set)

                try:
                    datastore.commit()
                except ConflictError:
                    datastore.abort()
                    datastore.sync()
                else:
                    break
        
            cms = self.context["cms"]
            for item in deleted_set:
                cms.item_deleted(
                    item = item,
                    user = user,
                    change = item.changes[-1]
                )

            self.go_back()
            
        elif self.action == "cancel":
            self.go_back()
    
    view_class = "sitebasis.views.BackOfficeDeleteView"

    @cached_getter
    def output(self):
        output = BaseBackOfficeController.output(self)
        output["delete_tree"] = self.delete_tree
        output["blocking_members"] = self.blocking_members
        return output

