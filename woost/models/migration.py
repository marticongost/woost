#-*- coding: utf-8 -*-
u"""Defines migrations to the database schema for woost.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from cocktail.persistence import MigrationStep

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
        for restriction in access_restrictions:
            try:
                del restriction._Configuration_access_restrictions
            except AttributeError:
                pass
        try:
            del config._access_restrictions
        except:
            pass

