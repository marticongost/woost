#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
import re
from cocktail import schema
from cocktail.translations import translations
from .configuration import Configuration
from .website import Website
from .file import File
from .publishable import Publishable
from .theme import Theme
from .metatags import MetaTags
from .localemember import LocaleMember
from .caching import CachingPolicy

translations.load_bundle("woost.models.settings")

def get_setting(key):
    return Configuration.instance.get_setting(key)

def add_setting(
    member,
    scopes = (Configuration, Website),
    related_end = "auto",
    inheritable = True
):
    member.is_setting = True
    if not member.custom_translation_key:
        member.custom_translation_key = "woost.models.settings." + member.name
    member.listed_by_default = False

    inherit_from_config = inheritable and Configuration in scopes

    for scope in scopes:
        scope_member = member.copy()
        scope_member.detach_from_source_member()

        if scope is Website and inherit_from_config:
            scope_member.default = None
            scope_member.required = False

        if (
            related_end
            and (
                (
                    isinstance(member, schema.Reference)
                    and not member.class_family
                )
                or (
                    isinstance(member, schema.Collection)
                    and isinstance(member.items, schema.Reference)
                    and not member.items.class_family
                )
            )
        ):
            if related_end == "auto":
                scope_member.related_end = schema.Collection()
            else:
                rel = related_end.copy()
                rel.detach_from_source_member()
                scope_member.related_end = rel

        scope.add_member(scope_member, append = True)

# Metadata and indexing
#------------------------------------------------------------------------------
add_setting(
    schema.Collection(
        "icons",
        items = schema.Reference(type = File),
        relation_constraints = [File.resource_type.equal("image")]
    )
)

add_setting(
    schema.Reference(
        "logo",
        type = File,
        relation_constraints = [File.resource_type.equal("image")]
    )
)

add_setting(
    schema.String(
        "keywords",
        translated = True,
        spellcheck = True,
        ui_form_control = "cocktail.ui.TextArea"
    )
)

add_setting(
    schema.String(
        "description",
        translated = True,
        spellcheck = True,
        ui_form_control = "cocktail.ui.TextArea"
    )
)

add_setting(
    MetaTags("meta_tags"),
    inheritable = False
)

add_setting(
    schema.Boolean(
        "robots_should_index",
        required = True,
        default = True
    )
)

# Contact
#------------------------------------------------------------------------------
add_setting(
    schema.String(
        "organization_name",
        translated = True
    )
)

add_setting(
    schema.URL(
        "organization_url"
    )
)

add_setting(
    schema.String(
        "address",
        ui_form_control = "cocktail.ui.TextArea"
    )
)

add_setting(
    schema.String(
        "town",
        translated = True
    )
)

add_setting(
    schema.String(
        "region",
        translated = True
    )
)

add_setting(
    schema.String(
        "postal_code"
    )
)

add_setting(
    schema.String(
        "country",
        translated = True
    )
)

add_setting(
    schema.String(
        "phone_number"
    )
)

add_setting(
    schema.String(
        "fax_number"
    )
)

add_setting(
    schema.EmailAddress(
        "email"
    )
)

add_setting(
    schema.EmailAddress(
        "technical_contact_email"
    )
)

# Cache
#------------------------------------------------------------------------------
add_setting(
    schema.Collection(
        "caching_policies",
        items = schema.Reference(type = CachingPolicy),
        bidirectional = True,
        integral = True
    )
)

# Special pages
#------------------------------------------------------------------------------
add_setting(
    schema.Reference(
        "home",
        type = Publishable,
        required = True
    ),
    scopes = [Website],
    related_end = schema.Reference(block_delete = True)
)

add_setting(
    schema.Reference(
        "login_page",
        type = Publishable
    )
)

add_setting(
    schema.Reference(
        "generic_error_page",
        type = Publishable
    )
)

add_setting(
    schema.Reference(
        "not_found_error_page",
        type = Publishable
    )
)

add_setting(
    schema.Reference(
        "gone_error_page",
        type = Publishable
    )
)

add_setting(
    schema.Reference(
        "forbidden_error_page",
        type = Publishable
    )
)

# Maintenance
#------------------------------------------------------------------------------
add_setting(
    schema.Boolean(
        "down_for_maintenance",
        required = True,
        default = False
    )
)

add_setting(
    schema.Reference(
        "maintenance_page",
        type = Publishable
    )
)

add_setting(
    schema.Collection(
        "maintenance_addresses",
        items = schema.String(),
        searchable = False
    )
)

# Languages
#------------------------------------------------------------------------------
add_setting(
    schema.Collection(
        "languages",
        items = schema.String(
            format = "^[a-z]{2}(-[A-Z]{2})?(-[a-z]+)?$"
        ),
        min = 1,
        searchable = False
    ),
    scopes = [Configuration]
)

add_setting(
    schema.Collection(
        "virtual_languages",
        items = schema.String(),
        searchable = False
    ),
    scopes = [Configuration]
)


add_setting(
    schema.Collection(
        "fallback_languages",
        items = (
            schema.Tuple(
                items = (
                    schema.String(),
                    schema.Collection(
                        type = tuple,
                        items = schema.String(),
                        request_value_separator = ","
                    )
                ),
                request_value_separator = ":"
            )
        ),
        request_value_separator = "\n",
        searchable = False,
        ui_form_control = "cocktail.ui.TextArea"
    ),
    scopes = [Configuration]
)

add_setting(
    schema.Collection(
        "published_languages",
        items = schema.String(),
        searchable = False
    )
)

add_setting(
    schema.String(
        "default_language",
        required = True,
        text_search = False,
        searchable = False
    )
)

add_setting(
    schema.Boolean(
        "heed_client_language",
        required = True,
        default = True,
        listed_by_default = False,
        member_group = "language"
    )
)

add_setting(
    LocaleMember(
        "backoffice_language",
        required = True,
        enumeration = ["en", "es", "ca"],
        default = "en",
        text_search = False
    ),
    scopes = [Configuration]
)

add_setting(
    schema.Collection(
        "backoffice_language_chain",
        items = schema.String(),
        searchable = False
    ),
    scopes = [Configuration]
)

# Look and feel
#------------------------------------------------------------------------------
add_setting(
    schema.Reference(
        "theme",
        type = Theme
    )
)

add_setting(
    schema.CodeBlock(
        "global_styles",
        language = "scss",
        listed_by_default = False,
        member_group = "presentation.appearence"
    )
)

# HTTPS
#------------------------------------------------------------------------------
add_setting(
    schema.String(
        "https_policy",
        required = True,
        default = "never",
        enumeration = [
            "always",
            "never",
            "per_page",
        ]
    )
)

add_setting(
    schema.Boolean(
        "https_persistence",
        required = True,
        default = False
    )
)

# System
#------------------------------------------------------------------------------
add_setting(
    schema.String(
        "timezone",
        required = False,
        format = re.compile(r'^["GMT"|"UTC"|"PST"|"MST"|"CST"|"EST"]{3}$|^[+-]\d{4}$'),
        text_search = False
    )
)

add_setting(
    schema.String(
        "smtp_host",
        default = "localhost",
        listed_by_default = False,
        text_search = False,
        member_group = "system.smtp"
    )
)

add_setting(
    schema.String(
        "smtp_user",
        text_search = False
    )
)

add_setting(
    schema.String(
        "smtp_password",
        text_search = False
    )
)

