#-*- coding: utf-8 -*-
u"""Defines migrations to the database schema for woost.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from cocktail.persistence import MigrationStep
from cocktail.persistence.utils import remove_broken_type

def admin_members_restriction(members):
    
    def add_permission(e):

        from woost.models import Role, ModifyMemberPermission
        
        everybody_role = Role.require_instance(qname = "woost.everybody")
        permission = ModifyMemberPermission(
            matching_members = list(members),
            authorized = False
        )
        permission.insert()
        
        for i, p in enumerate(everybody_role.permissions):
            if isinstance(p, ModifyMemberPermission) and p.authorized:
                everybody_role.permissions.insert(i, permission)
                break
        else:
            everybody_role.permissions.append(permission)

    return add_permission

#------------------------------------------------------------------------------

step = MigrationStep("added woost.models.Document.robots_*")

step.executing.append(
    admin_members_restriction([
        "woost.models.document.Document.robots_should_index",
        "woost.models.document.Document.robots_should_follow"
    ])
)

@step.processor("woost.models.document.Document")
def set_defaults(document):
    if not hasattr(document, "_robots_should_index"):
        document.robots_should_index = True
        document.robots_should_follow = True

#------------------------------------------------------------------------------

step = MigrationStep("added woost.models.Publishable.requires_https")

step.executing.append(
    admin_members_restriction([
        "woost.models.publishable.Publishable.requires_https"
    ])
)

@step.processor("woost.models.publishable.Publishable")
def set_defaults(publishable):
    if not hasattr(publishable, "_requires_https"):
        publishable.requires_https = False


#------------------------------------------------------------------------------

step = MigrationStep("make Product extend Publishable")

@when(step.executing)
def update_keys(e):
    from woost.extensions.shop import ShopExtension

    if ShopExtension.enabled:
        from cocktail.translations import translations
        from woost.models import Publishable
        from woost.extensions.shop import create_product_controller
        from woost.extensions.shop.product import Product

        # Update the publishable keys
        Publishable.keys.update([product.id for product in Product.select()])

        # Create the product controller
        create_product_controller()

#------------------------------------------------------------------------------

step = MigrationStep("use TranslationMapping to translations")

@when(step.executing)
def update_translations(e):
    from cocktail.schema import TranslationMapping
    from cocktail.persistence import PersistentObject

    def translated_items(schema):
        if schema.translated and schema.indexed:
            for item in schema.select():
                yield item
        else:
            for derived_schema in schema.derived_schemas(False):
                for item in translated_items(derived_schema):
                    yield item

    for item in translated_items(PersistentObject):
        translations = TranslationMapping(
            owner = item, 
            items = item.translations._items
        )
        item.translations._items = translations
        item._p_changed = True

    PersistentObject.rebuild_indexes(True)

#------------------------------------------------------------------------------

step = MigrationStep(
    "rename EmailTemplate.embeded_images to EmailTemplate.attachments"
)

step.rename_member(
    "woost.models.EmailTemplate",
    "embeded_images",
    "attachments"
)

#------------------------------------------------------------------------------

step = MigrationStep(
    "Apply full text indexing to elements with no translations"
)

@when(step.executing)
def rebuild_full_text_index(e):
    from woost.models import Item
    Item.rebuild_full_text_indexes(True)

#------------------------------------------------------------------------------

step = MigrationStep(
    "Replace EmailTemplate.attachments with EmailTemplate.initialization_code"
)

@when(step.executing)
def relocate_attachments_code(e):
    from woost.models import EmailTemplate

    for email_template in EmailTemplate.select():
        code = getattr(email_template, "_attachments", None)
        if code:
            del email_template._attachments
            if email_template.initialization_code:
                code = email_template.initialization_code + "\n\n" + code
            email_template.initialization_code = code

#------------------------------------------------------------------------------

step = MigrationStep(
    "Added the Role.implicit member"
)

@when(step.executing)
def flag_implicit_roles(e):
    from woost.models import Role

    implicit_roles_qnames = set((
        "woost.anonymous",
        "woost.everybody",
        "woost.authenticated"
    ))

    for role in Role.select():
        role.implicit = (role.qname in implicit_roles_qnames)

#------------------------------------------------------------------------------
 
step = MigrationStep("Removed the File.local_path member")

@step.processor("woost.models.file.File")
def remove_file_local_path_values(file):
    try:
        del file._local_path
    except:
        pass

@step.processor("woost.models.permission.MemberPermission")
def remove_permissions_for_file_local_path(permission):
    try:
        permission.matching_members.remove("woost.models.file.File.local_path")
    except:
        pass

#------------------------------------------------------------------------------

step = MigrationStep("Added the Style.applicable_to_text member")

@when(step.executing)
def index_style_applicable_to_text_member(e):
    from woost.models import Style
    Style.applicable_to_text.rebuild_index()

#------------------------------------------------------------------------------

step = MigrationStep(
    "Replaced CachingPolicy.cache_expiration with "
    "CachingPolicy.expiration_expression"
)

@step.processor("woost.models.caching.CachingPolicy")
def replace_cache_expiration_with_expiration_expression(policy):
    expiration = getattr(policy, "_cache_expiration", None)
    if expiration is not None:
        policy.expiration_expression = "expiration = %s" % expiration
        del policy._cache_expiration

#------------------------------------------------------------------------------

step = MigrationStep("Add multisite support")

@when(step.executing)
def add_multisite_support(e):
    from cocktail.persistence import datastore
    from woost.models import Configuration, Website, Item
    root = datastore.root

    # Remove all back-references from the Site and Language models
    for item in Item.select():
        for key in dir(item):
            if (
                key == "_site"
                or key.startswith("_Site_")
                or key.startswith("_Language_")
            ):
                delattr(item, key)

    # Remove the instance of Site from the database
    site_id = list(Item.qname.index.values(key = "woost.main_site"))[0]
    site = Item.index[site_id]
    site_state = site.__Broken_state__.copy()
    site_state["translations"] = dict(
        (lang, translation.__Broken_state__.copy())
        for lang, translation in site_state.pop("_translations").iteritems()
    )
    Item.index.remove(site_id)
    Item.keys.remove(site_id)

    # Create the configuration object
    config = Configuration()
    config.qname = "woost.configuration"
    config.insert()

    # Create a website
    website = Website()
    website.insert()
    website.hosts = ["localhost"]
    config.websites.append(website)

    # Languages
    published_languages = []

    for lang_id in root["woost.models.language.Language-keys"]:
        language = Item.index[lang_id]
        Item.index.remove(lang_id)
        Item.keys.remove(lang_id)
        language_state = language.__Broken_state__
        config.languages.append(language_state["_iso_code"])
        if language_state["_enabled"]:
            published_languages.append(language_state["_iso_code"])

    if list(config.languages) != published_languages:
        config.published_languages = published_languages

    # Delete old indexes from the database
    for key in list(root):
        if (
            key.startswith("woost.models.site.Site")
            or key.startswith("woost.models.language.Language")
        ):
            del root[key]

    # Settings that now belong in Configuration, as attributes
    config.secret_key = site_state.pop("secret_key")

    # Settings that now belong in Configuration, as regular fields
    for key in (        
        "login_page",
        "generic_error_page",
        "not_found_error_page",
        "forbidden_error_page",
        "default_language",
        "backoffice_language",
        "heed_client_language",
        "timezone",
        "smtp_host",
        "smtp_user",
        "smtp_password"
    ):
        config.set(key, site_state.pop("_" + key))

    # Settings that now belong in Configuration, as collections
    for key in (
        "publication_schemes",
        "caching_policies",
        "renderers",
        "image_factories",
        "triggers"
    ):
        config.set(key, list(site_state.pop("_" + key)))

    # Settings that now belong in Website, becoming translated fields
    for key in (
        "town",
        "region",
        "country"
    ):
        value = site_state.pop("_" + key)
        for lang in config.languages:
            website.set(key, value, lang)

    # Settings that now belong in website, as translated fields
    for key in (
        "site_name",
        "organization_name",
        "keywords",
        "description"
    ):
        for lang, translation_state in site_state["translations"].iteritems():
            value = translation_state.pop("_" + key)
            website.set(key, value, lang)

    # Settings that now belong in website, as regular fields
    for key in (
        "logo",
        "icon",
        "home",
        "organization_url",
        "address",
        "postal_code",
        "phone_number",
        "fax_number",
        "email",
        "https_policy",
        "https_persistence"
    ):
        website.set(key, site_state.pop("_" + key))

    # Extension specific changes
    from woost.extensions.blocks import BlocksExtension
    if BlocksExtension.instance.enabled:
        config.common_blocks = list(site_state.pop("_common_blocks"))

    from woost.extensions.audio import AudioExtension
    if AudioExtension.instance.enabled:
        config.audio_encoders = list(site_state.pop("_audio_encoders"))
        config.audio_decoders = list(site_state.pop("_audio_decoders"))

    from woost.extensions.mailer import MailerExtension
    if MailerExtension.instance.enabled:
        from woost.extensions.mailer.mailing import Mailing
        for mailing in Mailing.select():
            language = mailing._language
            if language:
                mailing._language = language.__Broken_state__["_iso_code"]

    from woost.extensions.googleanalytics import GoogleAnalyticsExtension
    if GoogleAnalyticsExtension.instance.enabled:
        account = GoogleAnalyticsExtension.instance._account
        del GoogleAnalyticsExtension.instance._account
        config.google_analytics_account = account

    # Rebuild all indexes
    Item.rebuild_indexes()

    # Preserve the remaining state
    datastore.root["woost.models.migration.multisite_leftovers"] = site_state

#------------------------------------------------------------------------------
step = MigrationStep("Store hashes using hexadecimal characters")

@when(step.executing)
def transform_hashes(e):
    from woost.models import File, User
    to_hex_string = lambda s: "".join(("%x" % ord(c)).zfill(2) for c in s)

    for file in File.select():
        file._file_hash = to_hex_string(file.file_hash)

    for user in User.select():
        if user.password:
            user._password = to_hex_string(user.password)

#------------------------------------------------------------------------------
step = MigrationStep("Assign global object identifiers")

@when(step.executing)
def assign_global_identifiers(e):
    from woost import app
    from woost.models import Item
    from woost.models.synchronization import rebuild_manifest

    for item in Item.select():
        item._global_id = app.installation_id + "-" + str(item.id)

    Item.global_id.rebuild_index()
    Item.synchronizable.rebuild_index()
    rebuild_manifest(True)

#------------------------------------------------------------------------------
step = MigrationStep("Expose models that where hidden in the Configuration model")

@when(step.executing)
def expose_hidden_configuration(e):
    from woost.models import Configuration
    
    config = Configuration.instance

    # restrictedaccess extension
    access_restrictions = getattr(config, "_access_restrictions", None)
    if access_restrictions:
        for restriction in access_restriction:
            try:
                del restriction._Configuration_access_restrictions
            except AttributeError:
                pass
        try:
            del config._access_restrictions
        except:
            pass

#------------------------------------------------------------------------------

step = MigrationStep("Remove the Action model")

@when(step.executing)
def remove_action_model(e):

    from cocktail.persistence import datastore
    from woost.models import Change

    root = datastore.root
    root.pop("woost.models.action.Action-keys", None)
    root.pop("woost.models.action.Action.id", None)
    root.pop("woost.models.action.Action.identifier", None)
    root.pop("woost.models.action.Action.title", None)

    for change in Change.select():
        change.action = change.action.__Broken_state__["_identifier"]

#------------------------------------------------------------------------------

step = MigrationStep("Remove the workflow extension")

@when(step.executing)
def remove_workflow_extension(e):

    from cocktail.persistence import datastore
    from woost.models import Item, Extension

    for extension in Extension.select():
        bp = getattr(extension, "__Broken_Persistent__", None)

        if bp is not None and bp.__name__ == "WorkflowExtension":
            id = extension.__Broken_state__["_id"]

            try:
                Item.index.remove(id, None)
            except KeyError:
                pass

            try:
                Item.keys.remove(id)
            except KeyError:
                pass

            try:
                Extension.keys.remove(id)
            except KeyError:
                pass

            break

            for member in Extension.members().itervalues():
                if member.indexed:
                    member.rebuild_index()

    for key in list(datastore.root):
        if key.startswith("woost.extensions.workflow"):
            datastore.root.pop(key)

#------------------------------------------------------------------------------

step = MigrationStep("Removed drafts")

@when(step.executing)
def remove_drafts(e):
 
    from cocktail.persistence import datastore
    from woost.models import (
        Item,
        Permission,
        ContentPermission,
        MemberPermission,
        Trigger,
        ContentTrigger
    )
    from woost.models.utils import remove_broken_type

    remove_broken_type(
        "woost.models.permission.ConfirmDraftPermission",
        existing_bases = (
            Item,
            Permission,
            ContentPermission
        )
    )

    remove_broken_type(
        "woost.models.permission.ConfirmDraftPermission",
        existing_bases = (
            Item,
            Trigger,
            ContentTrigger
        )
    )

    for item in Item.select():
        for key in "_is_draft", "_draft_source", "_drafts":
            try:
                delattr(item, key)
            except AttributeError:
                pass

    datastore.root.pop("woost.models.item.Item.is_draft", None)
    datastore.root.pop("woost.models.item.Item.draft_source", None)

    for permission in MemberPermission.select():
        for key in ("drafts", "draft_source", "is_draft"):
            key = "woost.models.item.Item." + key
            if key in permission.matching_members:
                permission.matching_members.remove(key)

#------------------------------------------------------------------------------

step = MigrationStep(
    "Change the qualified name of the password reset email template"
)

@when(step.executing)
def change_qname_of_password_reset_email_template(e):

    from woost.models import EmailTemplate

    template = EmailTemplate.get_instance(
        qname = "woost.views.password_change_confirmation_email_template"
    )

    if template:
        template.qname = "woost.password_change_email_template"

#------------------------------------------------------------------------------

step = MigrationStep("Move the blocks extension into the woost core")

@when(step.executing)
def move_blocks_to_core(e):
    
    from cocktail.persistence import datastore
    from woost.models import Item, Page, Template, Block, TextBlock
    from woost.models.rendering import Renderer

    # Rename keys
    for key in list(datastore.root):
        if key.startswith("woost.extensions.blocks."):
            new_key = key.replace(".extensions.blocks.", ".models.")
            datastore.root[new_key] = datastore.root.pop(key)

    # Consolidate StandardPage and BlocksPage into the new Page model
    for block in Block.select():
        try:
            pages = block._BlocksPage_blocks
        except AttributeError:
            pass
        else:
            block._Page_blocks = pages        
            del block._BlocksPage_blocks

    page_ids = datastore.root.pop("woost.models.standardpage.StandardPage-keys")

    if page_ids:
        for id in page_ids:
            Page.keys.add(id)
            page = Page.get_instance(id)
            page._p_changed = True

            block = TextBlock()

            for lang, trans in page.translations.iteritems():
                if hasattr(trans, "_body"):
                    block.set("text", trans._body, lang)
                    del trans._body

            page.blocks.append(block)
            block.insert()

    page_ids = datastore.root.pop("woost.models.blockspage.BlocksPage-keys")

    if page_ids:
        for id in page_ids:
            Page.keys.add(id)

    # Update references to the old template for block pages
    for template in Template.select():
        if template.identifier == "woost.extensions.blocks.BlocksPageView":
            template.identifier = "woost.views.StandardView"

    # Fix the name in the related end for Page.blocks
    for block in Block.select():
        block.Page_blocks._PersistentRelationCollection__member_name = \
            "Page_blocks"

#------------------------------------------------------------------------------
 
step = MigrationStep("Remove the Item.owner field")

@when(step.executing)
def remove_owner_field(e):

    from cocktail.persistence import datastore
    from woost.models import Item, ContentPermission, MemberPermission

    # Remove the owner value of every item
    for item in Item.select():
        try:
            del item._owner
        except AttributeError:
            pass

    # Drop the index for the member
    full_member_name = "woost.models.item.Item.owner"
    datastore.root.pop(full_member_name, None)

    # Purge all references to the owner member from member permissions
    for permission in MemberPermission.select():
        if permission.matching_members:
            member_count = len(permission.matching_members)
            try:
                permission.matching_members.remove(full_member_name)
            except (KeyError, ValueError):
                pass
            else:
                if member_count == 1:
                    permission.delete()

    # Purge the 'owned-items' expression from all permissions
    for permission in ContentPermission.select():
        matching_items = permission.matching_items
        if matching_items:
            try:
                filter = permission.matching_items["filter"]
            except KeyError:
                pass
            else:
                if filter == "owned-items" or (
                    hasattr(filter, "__contains__")
                    and "owned-items" in filter
                ):
                    permission.delete()

#------------------------------------------------------------------------------

step = MigrationStep("Remove the Document.attachments member")

@when(step.executing)
def remove_attachments_member(e):

    from woost.models import Document, File, MemberPermission

    for document in Document.select():
        try:
            del document._attachments
        except AttributeError:
            pass

    for file in File.select():
        try:
            del file._Document_attachments
        except AttributeError:
            pass

    full_member_name = "woost.models.document.Document.attachment"

    for permission in MemberPermission.select():
        if permission.matching_members:
            member_count = len(permission.matching_members)
            try:
                permission.matching_members.remove(full_member_name)
            except (KeyError, ValueError):
                pass
            else:
                if member_count == 1:
                    permission.delete()

#------------------------------------------------------------------------------

step = MigrationStep("Remove per document resources")

@when(step.executing)
def remove_document_resources(e):

    from woost.models import Publishable, Document, MemberPermission

    for document in Document.select():

        try:
            del document._branch_resources
        except AttributeError:
            pass
        
        try:
            del document._page_resources
        except AttributeError:
            pass

    for publishable in Publishable.select():

        try:
            del publishable._Document_branch_resources
        except AttributeError:
            pass

        try:
            del publishable._Document_page_resources
        except AttributeError:
            pass

        try:
            del publishable._inherit_resources
        except AttributeError:
            pass

    members = (
        "woost.models.document.Document.branch_resources",
        "woost.models.document.Document.page_resources",
        "woost.models.publishable.Publishable.inherit_resources"
    )

    for permission in MemberPermission.select():
        if permission.matching_members:
            removed = False

            for full_member_name in members:
                try:
                    permission.matching_members.remove(full_member_name)
                except (KeyError, ValueError):
                    pass
                else:
                    removed = True

            if removed and not permission.matching_members:
                permission.delete()

#------------------------------------------------------------------------------
 
step = MigrationStep("Remove Template.engine")

@when(step.executing)
def remove_template_engine(e):

    from woost.models import Template
    
    for template in Template.select():
        try:
            del template._engine
        except AttributeError:
            pass

#------------------------------------------------------------------------------
 
step = MigrationStep("Remove publication schemes")

@when(step.executing)
def remove_publication_schemes(e):

    from cocktail.persistence import datastore
    from woost.models import (
        Item,
        Configuration
    )
    from woost.models.utils import remove_broken_type

    remove_broken_type(
        "woost.models.publicationschemes.PublicationScheme",
        existing_bases = (
            Item,
        )
    )

    remove_broken_type(
        "woost.models.publicationschemes.HierarchicalPublicationScheme",
        existing_bases = (
            Item,
        )
    )

    remove_broken_type(
        "woost.models.publicationschemes.IdPublicationScheme",
        existing_bases = (
            Item,
        )
    )

    remove_broken_type(
        "woost.models.publicationschemes.DescriptiveIdPublicationScheme",
        existing_bases = (
            Item,
        )
    )

    try:
        del Configuration.instance._publication_schemes
    except AttributeError:
        pass

