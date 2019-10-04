"""Defines migrations to the database schema for woost.

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from collections import defaultdict

from cocktail.persistence import migration_step


#------------------------------------------------------------------------------
# Migrations for Woost2 projects
#------------------------------------------------------------------------------


@migration_step
def convert_indexes_to_python3(e):

    from ZODB.broken import Broken
    from cocktail.persistence import (
        PersistentObject,
        SingleValueIndex,
        migrate,
        datastore
    )

    broken_objects = defaultdict(dict)
    datastore.root["woost2_broken_objects"] = broken_objects

    model_keys = [
        v for k, v in datastore.root.items()
        if k.endswith("-keys")
    ]

    for cls in PersistentObject.derived_schemas(False):
        if not cls.indexed:
            continue
        prev_index = cls.index
        if not hasattr(prev_index, "__Broken_state__"):
            continue
        index = SingleValueIndex()
        cls.index = index
        for key, value in prev_index.__Broken_state__["_SingleValueIndex__items"].items():
            if isinstance(value, Broken):
                broken_cls = value.__Broken_Persistent__
                broken_name = f"{broken_cls.__module__}.{broken_cls.__name__}"
                broken_objects[broken_name][key] = value.__Broken_state__
                for keys in model_keys:
                    try:
                        keys.remove(key)
                    except KeyError:
                        pass
            else:
                index.add(key, value)


@migration_step
def rebuild_indexes_after_conversion_to_python3(e):

    from cocktail.persistence import (
        PersistentObject,
        full_text_indexing_disabled
    )

    with full_text_indexing_disabled():
        PersistentObject.rebuild_indexes(True)

    PersistentObject.rebuild_full_text_indexes(
        recursive=True,
        verbose=True
    )


@migration_step
def remove_woost2_models(e):

    # Create dummy modules / classes to workaround serialization errors when
    # committing
    import sys
    from importlib import import_module
    from types import ModuleType
    from cocktail.persistence import datastore
    from woost.models import Permission, Role, Publishable
    from woost.models.utils import remove_broken_type

    broken_types = (
        (
            "woost.models.siteinstallation",
            (
                "SiteInstallation",
                {
                    "name": "InstallationSyncPermission",
                    "existing_bases": (Permission,)
                }
            )
        ),
        (
            "woost.models.trigger",
            (
                "Trigger",
                "ContentTrigger",
                "CreateTrigger",
                "InsertTrigger",
                "ModifyTrigger",
                "DeleteTrigger"
            )
        ),
        (
            "woost.models.triggerresponse",
            (
                "TriggerResponse",
                "CustomTriggerResponse",
                "SendEmailTriggerResponse"
            )
        ),
        (
            "woost.models.feed", (
                {
                    "name": "Feed",
                    "existing_bases": (Publishable,)
                },
            )
        ),
        ("woost.models.userview", ("UserView",)),
        ("woost.models.extension", ("Extension",)),
        ("woost.extensions.shop", ("ShopExtension",)),
        ("woost.extensions.countries", ("CountriesExtension",)),
        ("woost.extensions.payments", ("PaymentsExtension",)),
        ("woost.extensions.comments", ("CommentsExtension",)),
        ("woost.extensions.recaptcha", ("ReCaptchaExtension",)),
        ("woost.extensions.staticsite", ("StaticSiteExtension",)),
        ("woost.extensions.sitemap", ("SitemapExtension",)),
        ("woost.extensions.pdf", ("PDFExtension",)),
        ("woost.extensions.vimeo", ("VimeoExtension",)),
        ("woost.extensions.signup", ("SignUpExtension",)),
        ("woost.extensions.googlesearch", ("GoogleSearchExtension",)),
        ("woost.extensions.googleanalytics", ("GoogleAnalyticsExtension",)),
        ("woost.extensions.googletagmanager", ("GoogleTagManagerExtension",)),
        ("woost.extensions.campaignmonitor", ("CampaignMonitorExtension",)),
        ("woost.extensions.mailer", ("MailerExtension",)),
        ("woost.extensions.usermodels", ("UserModelsExtension",)),
        ("woost.extensions.locations", ("LocationsExtension",)),
        ("woost.extensions.webconsole", ("WebConsoleExtension",)),
        ("woost.extensions.blocks", ("BlocksExtension",)),
        ("woost.extensions.opengraph", ("OpenGraphExtension",)),
        ("woost.extensions.ecommerce", ("ECommerceExtension",)),
        ("woost.extensions.facebookpublication", ("FacebookPublicationExtension",)),
        ("woost.extensions.shorturls", ("ShortURLsExtension",)),
        ("woost.extensions.twitterpublication", ("TwitterPublicationExtension",)),
        ("woost.extensions.textfile", ("TextFileExtension",)),
        ("woost.extensions.audio", ("AudioExtension",)),
        ("woost.extensions.issuu", ("IssuuExtension",)),
        ("woost.extensions.campaign3", ("CampaignMonitor3Extension",)),
        ("woost.extensions.youtube", ("YouTubeExtension",)),
        ("woost.extensions.tv3alacarta", ("TV3ALaCartaExtension",)),
        ("woost.extensions.externalfiles", ("ExternalFilesExtension",)),
        ("woost.extensions.restrictedaccess", ("RestrictedAccessExtension",)),
        ("woost.extensions.annotations", ("AnnotationsExtension",)),
        ("woost.extensions.notices", ("NoticesExtension",)),
        ("woost.extensions.variables", ("VariablesExtension",)),
        ("woost.extensions.surveys", ("SurveysExtension",)),
        ("woost.extensions.newsletters", ("NewslettersExtension",)),
        ("woost.extensions.forms", ("FormsExtension",)),
        ("woost.extensions.translationworkflow", ("TranslationWorkflowExtension",)),
        ("woost.extensions.identity", ("IdentityExtension",)),
        ("woost.extensions.attributes", ("AttributesExtension",)),
        ("woost.extensions.staticpub", ("StaticPubExtension",)),
        ("woost.extensions.nocaptcha", ("NoCaptchaExtension",))
    )

    from woost.models import Item
    from woost.models.utils import remove_broken_type

    for mod_name, classes in broken_types:
        try:
            mod = import_module(mod_name)
        except ImportError:
            mod = ModuleType(mod_name)
            sys.modules[mod_name] = mod

        for cls_spec in classes:
            if isinstance(cls_spec, str):
                cls_name = cls_spec
            else:
                cls_name = cls_spec["name"]
            cls = type(cls_name, (object,), {})
            cls.__module__ = mod_name
            setattr(mod, cls_name, cls)

    for mod_name, classes in broken_types:

        for cls_spec in classes:
            if isinstance(cls_spec, str):
                cls_name = cls_spec
                kwargs = {}
            else:
                cls_name = cls_spec.pop("name")
                kwargs = cls_spec

            kwargs.setdefault("existing_bases", (Item,))
            remove_broken_type(mod_name + "." + cls_name, **kwargs)

    # Delete the object manifest
    try:
        del datastore.root["woost.manifest"]
    except KeyError:
        pass

    # Delete the Item.synchronizable member
    try:
        del datastore.root["woost.models.Item.synchronizable"]
    except KeyError:
        pass

    for item in Item.select():
        try:
            del item._synchronizable
        except AttributeError:
            pass

    # Delete the Role.user_views member
    for role in Role.select():
        try:
            del role._user_views
        except AttributeError:
            pass


@migration_step
def add_site_identifiers(e):

    from woost.models import Website

    for n, website in enumerate(Website.select()):

        if website.hosts:
            parts = website.hosts[0].split(".")
            if parts[0] == "www":
                parts.pop(0)

            # Pop TLDs; very rough, but including the full list of TLDs would
            # be overkill
            if len(parts) >= 2:
                parts.pop(-1)

            identifier = "-".join(parts)
        else:
            identifier = "website%d" % n

        website.identifier = identifier


@migration_step
def remove_configuration_image_factories(e):

    from woost.models import Configuration, MemberPermission
    from woost.models.rendering import ImageFactory

    key = "woost.models.configuration.Configuration.image_factories"
    for perm in MemberPermission.select():
        if perm.matching_members and key in perm.matching_members:
            perm.matching_members.remove(key)

    del Configuration.instance._image_factories

    for img_factory in ImageFactory.select():
        try:
            del img_factory._Configuration_image_factories
        except AttributeError:
            pass


@migration_step
def remove_configuration_renderers(e):

    from woost.models import Configuration, MemberPermission
    from woost.models.rendering import Renderer

    key = "woost.models.configuration.Configuration.renderers"
    for perm in MemberPermission.select():
        if perm.matching_members and key in perm.matching_members:
            perm.matching_members.remove(key)

    del Configuration.instance._renderers

    for renderer in Renderer.select():
        try:
            del renderer._Configuration_renderers
        except AttributeError:
            pass


@migration_step
def remove_configuration_video_player_settings(e):

    from woost.models import Configuration, VideoPlayerSettings, MemberPermission

    key = "woost.models.configuration.Configuration.video_player_settings"
    for perm in MemberPermission.select():
        if perm.matching_members and key in perm.matching_members:
            perm.matching_members.remove(key)

    del Configuration.instance._video_player_settings

    for vid_player_settings in VideoPlayerSettings.select():
        del vid_player_settings._Configuration_video_player_settings


@migration_step
def remove_configuration_websites(e):

    from woost.models import Configuration, Website, MemberPermission

    key = "woost.models.configuration.Configuration.websites"
    for perm in MemberPermission.select():
        if perm.matching_members and key in perm.matching_members:
            perm.matching_members.remove(key)

    del Configuration.instance._websites

    for website in Website.select():
        try:
            del website._Configuration_websites
        except AttributeError:
            pass


@migration_step
def make_slots_integral_and_add_block_catalogs(e):

    from cocktail import schema
    from cocktail.translations import translations
    from woost.models import (
        Item,
        Slot,
        Configuration,
        Website,
        Block,
        BlocksCatalog,
        BlockClone
    )

    config = Configuration.instance

    def T(**values):
        return schema.TranslatedValues(
            **dict(
                (lang, v)
                for lang, v in values.items()
                if lang in config.languages
            )
        )

    catalog_blocks = set()
    catalog_slot_keys = set()

    def create_catalogs(
        source,
        qname_prefix,
        old_slots=(),
        website=None
    ):
        catalog_defs = list(old_slots)

        for member in source.__class__.iter_members():

            if isinstance(member, Slot):
                catalog_defs.append((
                    member.name,
                    {
                        "title": schema.TranslatedValues(
                            **dict(
                                (
                                    language,
                                    translations(member, language=language)
                                    + (
                                        (
                                            " - "
                                            + translations(
                                                website,
                                                language=language
                                            )
                                        )
                                        if website else ""
                                    )
                                )
                                for language in config.languages
                            )
                        )
                    }
                ))

        for slot_name, catalog_kwargs in catalog_defs:

            catalog = BlocksCatalog.new(**catalog_kwargs)

            if not catalog.qname:
                qname = qname_prefix + "." + slot_name
                if qname.endswith("_blocks"):
                    qname = qname[:-len("_blocks")]
                catalog.qname = qname

            blocks = getattr(source, "_" + slot_name, None)
            if blocks:
                catalog.blocks = list(blocks)

            catalog_slot_keys.add("_%s_%s" % (source.__class__.__name__, slot_name))

            for block in blocks:
                catalog_blocks.add(block)

    footer_def = (
        "footer_blocks", {
            "title": T(
                ca="Peu de pàgina",
                es="Pie de página",
                en="Footer"
            )
        }
    )

    create_catalogs(config, "woost.block_catalogs", [
        ("common_blocks", {
            "title": T(
                ca="Blocs comuns",
                es="Bloques comunes",
                en="Common blocks"
            )
        }),
        footer_def
    ])

    for website in Website.select():
        create_catalogs(
            website,
            website.identifier + ".block_catalogs",
            (footer_def,) if getattr(website, "_footer_blocks", None) else (),
            website = website
        )

    for block in catalog_blocks:
        for member in block.__class__.iter_members():
            related_end = getattr(member, "related_end", None)
            if (
                related_end
                and isinstance(related_end, Slot)
                and related_end.schema not in (
                    Configuration,
                    Website,
                    BlocksCatalog
                )
            ):
                referrals = getattr(block, "_" + member.name, None)
                if referrals is not None:
                    delattr(block, "_" + member.name)
                    for referrer in referrals:
                        clone = BlockClone.new()
                        clone.source_block = block
                        blocks = referrer.get(related_end)
                        index = blocks.index(block)
                        blocks._items[index] = clone

    # Slot related ends are now a single reference
    slot_keys = []

    for model in Item.schema_tree():
        if issubclass(model, (Configuration, Website, BlocksCatalog)):
            continue
        for member in model.iter_members(recursive=False):
            if isinstance(member, Slot):
                slot_keys.append("_" + member.related_end.name)

    for block in Block.select():
        for slot_key in slot_keys:
            value = getattr(block, slot_key, None)
            if value is not None and not isinstance(value, Item):
                if len(value) == 1:
                    setattr(block, slot_key, value[0])
                elif len(value) == 0:
                    setattr(block, slot_key, None)
                else:
                    raise ValueError("%s.%s contains too many blocks" % (
                        block,
                        slot_key
                    ))
        for slot_key in catalog_slot_keys:
            try:
                delattr(block, slot_key)
            except AttributeError:
                pass


@migration_step
def remove_role_hidden_content_types(e):

    from woost.models import Role

    for role in Role.select():
        try:
            del role._hidden_content_types
        except AttributeError:
            pass


@migration_step
def remove_role_default_content_type(e):

    from woost.models import Role

    for role in Role.select():
        try:
            del role._default_content_type
        except AttributeError:
            pass


@migration_step
def convert_user_roles_collection_to_single_reference(e):

    from woost.models import User

    for user in User.select():
        try:
            roles = user._roles
        except AttributeError:
            continue
        else:
            del user._roles
            if roles:
                if len(roles) > 1:
                    print(
                        "Users should have a single role; %r has %r. "
                        "Defaulted to the first role, original roles "
                        "accessible through the User._woost2_roles "
                        "property."
                        % (user, roles)
                    )
                    user._woost2_roles = list(roles)
                user._role = roles[0]
            else:
                user._role = None


@migration_step
def remove_login_controller(e):
    from woost.models import Controller
    controller = Controller.get_instance(qname="woost.login_controller")
    controller.delete()


@migration_step
def add_user_preferred_language(e):

    from woost.models import User

    for user in User.select():
        try:
            lang = user._prefered_language
        except AttributeError:
            # Apply defaults
            user.preferred_language
        else:
            user.preferred_language = lang


@migration_step
def create_admin(e):

    from woost.models import Document, Controller
    from woost.admin.initialization import create_admin

    old_admin = Document.get_instance(qname="woost.backoffice")
    if old_admin:
        old_admin.delete()

    old_admin_controller = Controller.get_instance(
        qname="woost.backoffice_controller"
    )
    if old_admin_controller:
        old_admin_controller.delete()

    create_admin()


#------------------------------------------------------------------------------
# Woost3 migrations
#------------------------------------------------------------------------------


@migration_step
def support_multiple_icons_per_website(e):

    from woost.models import Website

    for website in Website.select():
        try:
            icon = website._icon
        except AttributeError:
            pass
        else:
            del website._icon
            if icon:
                del icon._Website_icon
                website.icons.append(icon)

@migration_step
def copy_document_description_to_summary_and_meta_description(e):

    from woost.models import Document

    for doc in Document.select():
        for lang, trans in doc.translations.items():
            try:
                desc = trans._description
            except AttributeError:
                pass
            else:
                del trans._description
                if desc:
                    doc.set("summary", desc, lang)
                    doc.set("meta_description", desc, lang)


@migration_step
def create_general_role(e):

    from woost.models import Configuration
    from woost.models.initialization import SiteInitializer

    init = SiteInitializer()
    init.languages = Configuration.instance.languages
    init.create_general_role()

