#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from __future__ import with_statement
from base64 import b64encode
from cocktail.modeling import cached_getter, InstrumentedSet
from cocktail.controllers import context
from cocktail.controllers.webservices import (
    PersistentClassWebService,
    excluded_member
)
from sitebasis.models import (
    changeset_context,
    Item,
    User,
    Site,
    Language,
    allowed,
    restrict_access,
    reduce_ruleset,
    restricted_modification_context,
    AccessAllowedExpression
)
from sitebasis.controllers.basecmscontroller import BaseCMSController


class ItemWebService(PersistentClassWebService):
    root_type = Item

    def _init_user_collection(self, user_collection):
        PersistentClassWebService._init_user_collection(self, user_collection)
        user_collection.add_base_filter(AccessAllowedExpression(self.user))

    @cached_getter
    def languages(self):
        return Language.codes

    @cached_getter
    def user(self):
        return context["cms"].authentication.user

    class JSONEncoder(PersistentClassWebService.JSONEncoder):
        
        def get_member_value(self, obj, member, language = None):

            # Exclude the 'changes' member
            if member is Item.changes:
                value = excluded_member

            # Exclude restricted members
            elif not allowed(
                ruleset = self.ruleset,
                user = self.user,
                action = "read",
                target_instance = obj,
                target_member = member.name,
                language = language
            ):
                value = excluded_member
 
            # Special case for user passwords
            elif member is User.password:
                value = obj.password
                if value:
                    value = b64encode(value)            
            else:
                value = PersistentClassWebService.JSONEncoder.get_member_value(
                    self,
                    obj,
                    member,
                    language
                )

            return value

    @cached_getter
    def json_encoder(self):
        encoder = PersistentClassWebService.json_encoder(self)
        encoder.user = self.user
        encoder.ruleset = reduce_ruleset(
            Site.main.access_rules_by_priority,
            {
                "user": self.user,
                "action": "read",
                "target_type": self.type
            }
        )
        return encoder
    
    def _init_new_instance(self, instance):
        with restricted_modification_context(instance, self.user):
            PersistentClassWebService._init_new_instance(self, instance)

    def _store_new_instance(self, instance):
        if instance.is_draft:
            instance.insert()
        else:
            with changeset_context(author = self.user):
                instance.insert()

    def _update_instance(self, instance):

        user = self.user

        with restricted_modification_context(instance, user):
            if instance.is_draft:
                PersistentClassWebService._update_instance(self, instance)
            else:
                with changeset_context(author = user):
                    PersistentClassWebService._update_instance(self, instance)

    def _delete_instances(self, query):

        user = self.user

        authz_context = {
            "user": user,
            "action": "delete",
            "target_type": self.type
        }
        authz_context["ruleset"] = reduce_ruleset(
            Site.main.access_rules_by_priority,
            authz_context
        )
        
        class ValidatingDeletedSet(InstrumentedSet):
            def item_added(self, item):
                restrict_access(
                    target_instance = item,
                    **authz_context
                )

        deleted_set = ValidatingDeletedSet()

        with changeset_context(author = user):
            for item in list(query):
                item.delete(deleted_set)


class CMSWebServicesController(BaseCMSController):
    data = ItemWebService    

