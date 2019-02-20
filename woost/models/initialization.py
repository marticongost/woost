#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""

from random import choice
from optparse import OptionParser
from getpass import getpass
from cocktail.stringutils import random_string
from cocktail.translations import translations
from cocktail.iteration import first
from cocktail.persistence import (
    datastore,
    mark_all_migrations_as_executed,
    reset_incremental_id
)
from woost import app
from woost.models import (
    changeset_context,
    Item,
    Configuration,
    Website,
    Publishable,
    Document,
    Page,
    TextBlock,
    LoginBlock,
    CustomBlock,
    User,
    Role,
    URI,
    Controller,
    Theme,
    Template,
    Style,
    Grid,
    GridSize,
    File,
    Permission,
    ReadPermission,
    CreatePermission,
    ModifyPermission,
    DeletePermission,
    RenderPermission,
    ReadMemberPermission,
    ModifyMemberPermission,
    CreateTranslationPermission,
    DebugPermission,
    ReadTranslationPermission,
    ModifyTranslationPermission,
    DeleteTranslationPermission,
    ReadHistoryPermission,
    AccessLevel,
    EmailTemplate,
    CachingPolicy,
    VideoPlayerSettings,
    rendering
)
from woost.admin.initialization import create_admin

translations.load_bundle("woost.models.initialization")


class TranslatedValues(object):

    def __init__(self, key = None, **kwargs):
        self.key = key
        self.kwargs = kwargs


class SiteInitializer(object):

    admin_email = "admin@localhost"
    admin_password = ""
    languages = ["en"]
    extensions = []
    hosts = ["localhost"]
    base_id = None

    read_only_types = [
        Style,
        User,
        Template,
        EmailTemplate,
        rendering.Renderer,
        rendering.ImageFactory,
        VideoPlayerSettings
    ]

    restricted_types = [
        Role,
        Controller,
        Permission,
        CachingPolicy,
        Theme,
        Grid,
        GridSize
    ]

    read_only_members = [
        "woost.models.publishable.Publishable.mime_type",
        "woost.models.configuration.Configuration.login_page",
        "woost.models.configuration.Configuration.generic_error_page",
        "woost.models.configuration.Configuration.not_found_error_page",
        "woost.models.configuration.Configuration.forbidden_error_page",
        "woost.models.configuration.Configuration.maintenance_page",
        "woost.models.website.Website.login_page",
        "woost.models.website.Website.home",
        "woost.models.website.Website.generic_error_page",
        "woost.models.website.Website.not_found_error_page",
        "woost.models.website.Website.forbidden_error_page",
        "woost.models.website.Website.maintenance_page",
    ]

    restricted_members = [
        "woost.models.item.Item.qname",
        "woost.models.item.Item.global_id",
        "woost.models.publishable.Publishable.encoding",
        "woost.models.publishable.Publishable.login_page",
        "woost.models.publishable.Publishable.requires_https",
        "woost.models.configuration.Configuration.maintenance_addresses",
        "woost.models.configuration.Configuration.languages",
        "woost.models.configuration.Configuration.published_languages",
        "woost.models.configuration.Configuration.default_language",
        "woost.models.configuration.Configuration.heed_client_language",
        "woost.models.configuration.Configuration.timezone",
        "woost.models.configuration.Configuration.smtp_host",
        "woost.models.configuration.Configuration.smtp_user",
        "woost.models.configuration.Configuration.smtp_password",
        "woost.models.configuration.Configuration.theme",
        "woost.models.website.Website.hosts",
        "woost.models.website.Website.https_policy",
        "woost.models.website.Website.https_persistence",
        "woost.models.website.Website.published_languages",
        "woost.models.website.Website.default_language",
        "woost.models.website.Website.heed_client_language",
        "woost.models.website.Website.theme",
        "woost.models.block.Block.initialization"
    ]

    image_factories = [
        "default",
        "icon16",
        "icon32",
        "edit_blocks_thumbnail",
        "close_up",
        "default_thumbnail",
        "collage"
    ]

    def main(self):

        parser = OptionParser()
        parser.add_option("-u", "--user", help = "Administrator email")
        parser.add_option("-p", "--password", help = "Administrator password")
        parser.add_option("-l", "--languages",
            help = "Comma separated list of languages")
        parser.add_option("--hostname", help = "Hostname for the website")
        parser.add_option("-e", "--extensions",
            default = "",
            help = "The list of extensions to enable")
        parser.add_option("-b", "--base-id",
            type = int,
            help = "Seed the incremental ID sequence at a non-zero value")
        parser.add_option("-i", "--installation-id",
            default = "DEV",
            help = "A unique prefix for this installation, used to assign "
                   "globally unique identifiers for objects."
        )

        options, args = parser.parse_args()

        self.admin_email = options.user
        self.admin_password = options.password

        if self.admin_email is None:
            self.admin_email = input("Administrator email: ") or "admin@localhost"

        if self.admin_password is None:
            self.admin_password = getpass("Administrator password: ") \
                or random_string(8)

        if options.hostname:
            self.hosts = [options.hostname]

        languages = options.languages \
            and options.languages.replace(",", " ") \
            or input("Languages: ") or "en"

        self.languages = languages.split()
        self.extensions = options.extensions.split(",")
        self.base_id = options.base_id
        app.installation_id = options.installation_id

        self.initialize()

        print((
            "Your site has been successfully created. You can start it by "
            "executing the 'run.py' script. An administrator account for the "
            "content manager interface has been generated with email "
            "%s and the supplied password."
            % self.admin_email
        ))

    def initialize(self):
        self.reset_database()

        with changeset_context() as changeset:
            self.changeset = changeset
            self.create_content()

        mark_all_migrations_as_executed()
        datastore.commit()

    def reset_database(self):
        datastore.clear()
        datastore.close()

        if self.base_id:
            reset_incremental_id(self.base_id)

    def _create(self, _model, **values):
        instance = _model()

        for key, value in values.items():
            if isinstance(value, TranslatedValues):
                trans_key = "woost.initialization."

                if value.key:
                    trans_key += value.key
                else:
                    qname = values.get("qname")
                    if not qname:
                        raise ValueError(
                            "Can't translate the values for %s without "
                            "giving it a qname or providing an explicit "
                            "translation key"
                            % instance
                        )
                    prefix = "woost."
                    assert qname.startswith(prefix)
                    trans_key += qname[len(prefix):] + "." + key

                for language in self.languages:
                    trans = translations(trans_key, language, **value.kwargs)
                    if trans:
                        instance.set(key, trans, language)
            else:
                setattr(instance, key, value)

        instance.insert()
        return instance

    def create_content(self):

        # Bootstrap: create the site's configuration and administrator user
        self.configuration = self.create_configuration()
        self.administrator = self.create_administrator()

        self.configuration.author = self.administrator
        self.administrator.author = self.administrator

        # From this point, the authorship f or further objects is set
        # automatically through the active changeset
        self.changeset.author = self.administrator

        # Default website
        self.website = self.create_website()

        # Roles
        self.anonymous_role = self.create_anonymous_role()
        self.anonymous_user = self.create_anonymous_user()

        self.administrator_role = self.create_administrator_role()
        self.administrator.role = self.administrator_role

        self.everybody_role = self.create_everybody_role()
        self.authenticated_role = self.create_authenticated_role()
        self.editor_role = self.create_editor_role()

        self.editor_access_level = self.create_editor_access_level()

        # Standard theme
        self.configuration.theme = self.create_default_theme()

        # Templates and controllers
        self.create_controllers()

        self.configuration.default_page_template = \
            self.create_default_page_template()

        self.configuration.default_news_template = \
            self.create_default_news_template()

        self.configuration.default_event_template = \
            self.create_default_event_template()

        # Home page
        self.website.home = self.create_home()

        # Default stylesheets
        self.user_stylesheet = self.create_user_stylesheet()

        # Renderers
        self.content_renderer = self.create_content_renderer()
        self.icon16_renderer = self.create_icon16_renderer()
        self.icon32_renderer = self.create_icon32_renderer()

        # Image factories
        for image_factory_id in self.image_factories:
            key = image_factory_id + "_image_factory"
            method_name = "create_%s_image_factory" % image_factory_id
            method = getattr(self, method_name)
            image_factory = method()
            setattr(self, key, image_factory)

        # Backoffice
        self.backoffice = create_admin()

        # Error pages
        self.generic_error_page = self.create_generic_error_page()
        self.configuration.generic_error_page = self.generic_error_page

        self.not_found_error_page = self.create_not_found_error_page()
        self.configuration.not_found_error_page = self.not_found_error_page

        self.forbidden_error_page = self.create_forbidden_error_page()
        self.configuration.forbidden_error_page = self.forbidden_error_page

        # Password change
        self.password_change_page = self.create_password_change_page()
        self.password_change_confirmation_page = \
            self.create_password_change_confirmation_page()
        self.password_change_email_template = \
            self.create_password_change_email_template()

        # Login page
        self.login_page = self.create_login_page()
        self.configuration.login_page = self.login_page

    def create_configuration(self):
        config = self._create(
            Configuration,
            qname = "woost.configuration",
            secret_key = random_string(10),
            default_language = self.languages[0],
            languages = self.languages,
            backoffice_language =
                first(
                    language
                    for language in self.languages
                    if language in
                        Configuration.backoffice_language.enumeration
                )
        )
        config.footer_blocks = [
            self._create(
                CustomBlock,
                qname = "woost.vcard",
                heading = TranslatedValues(),
                view_class = "woost.views.VCard"
            )
        ]
        return config

    def create_administrator(self):
        return self._create(
            User,
            qname = "woost.administrator",
            email = self.admin_email,
            password = self.admin_password
        )

    def create_website(self):
        return self._create(
            Website,
            site_name = TranslatedValues("website.site_name"),
            identifier = self.hosts[0].split(".")[0],
            hosts = self.hosts
        )

    def create_anonymous_role(self):
        return self._create(
            Role,
            qname = "woost.anonymous",
            implicit = True,
            title = TranslatedValues()
        )

    def create_anonymous_user(self):
        return self._create(
            User,
            qname = "woost.anonymous_user",
            email = "anonymous@localhost",
            role = self.anonymous_role,
            anonymous = True
        )

    def create_administrator_role(self):
        return self._create(
            Role,
            qname = "woost.administrators",
            title = TranslatedValues(),
            permissions = [
                self._create(ReadPermission, content_type = Item),
                self._create(CreatePermission, content_type = Item),
                self._create(ModifyPermission, content_type = Item),
                self._create(DeletePermission, content_type = Item),
                self._create(ReadMemberPermission),
                self._create(ModifyMemberPermission),
                self._create(ReadHistoryPermission),
                self._create(DebugPermission)
            ]
        )

    def create_everybody_role(self):
        role = self._create(
            Role,
            implicit = True,
            qname = "woost.everybody",
            title = TranslatedValues(),
            permissions = [
                self._create(RenderPermission, content_type = Item),
                self._create(
                    ReadPermission,
                    content_type = Publishable,
                    content_expression =
                        "from woost.models import user_has_access_level\n"
                        "items.add_filter(user_has_access_level)"
                )
            ]
        )

        # Restrict readable members
        if self.restricted_members:
            role.permissions.append(
                self._create(
                    ReadMemberPermission,
                    authorized = False,
                    matching_members = self.restricted_members
                )
            )

        role.permissions.append(self._create(ReadMemberPermission))

        # Restrict modifiable members
        if self.read_only_members:
            role.permissions.append(
                self._create(
                    ModifyMemberPermission,
                    authorized = False,
                    matching_members = self.read_only_members
                )
            )

        role.permissions.append(self._create(ModifyMemberPermission))

        # All languages allowed
        role.permissions.extend([
            self._create(CreateTranslationPermission),
            self._create(ReadTranslationPermission),
            self._create(ModifyTranslationPermission),
            self._create(DeleteTranslationPermission)
        ])

        return role

    def create_authenticated_role(self):
        return self._create(
            Role,
            qname = "woost.authenticated",
            implicit = True,
            title = TranslatedValues()
        )

    def create_editor_role(self):
        role = self._create(
            Role,
            qname = "woost.editors",
            title = TranslatedValues()
        )

        # Restrict readable types
        if self.restricted_types:
            for restricted_type in self.restricted_types:
                for permission_type in (
                    ReadPermission,
                    CreatePermission,
                    ModifyPermission,
                    DeletePermission
                ):
                    role.permissions.append(
                        self._create(
                            permission_type,
                            authorized = False,
                            content_type = restricted_type
                        )
                    )

        # Restrict modifiable types
        if self.read_only_types:
            for read_only_type in self.read_only_types:
                for permission_type in (
                    CreatePermission,
                    ModifyPermission,
                    DeletePermission
                ):
                    role.permissions.append(
                        self._create(
                            permission_type,
                            authorized = False,
                            content_type = read_only_type
                        )
                    )

        for permission_type in (
            ReadPermission,
            CreatePermission,
            ModifyPermission,
            DeletePermission,
            ReadHistoryPermission
        ):
            role.permissions.append(
                self._create(
                    permission_type,
                    content_type = Item
                )
            )

        role.permissions.append(self._create(DebugPermission))

        return role

    def create_editor_access_level(self):
        return self._create(
            AccessLevel,
            qname = "woost.editor_access_level",
            roles_with_access = [self.editor_role]
        )

    def create_default_theme(self):
        return self._create(
            Theme,
            qname = "woost.default_theme",
            title = TranslatedValues(),
            identifier = "default",
            grid = self.create_default_grid()
        )

    def create_default_grid(self):
        return self._create(
            Grid,
            title = TranslatedValues(),
            qname = "woost.default_grid",
            column_count = 12,
            sizes = [
                self._create(
                    GridSize,
                    identifier = "XL",
                    min_width = 1389,
                    column_width = 80
                ),
                self._create(
                    GridSize,
                    identifier = "L",
                    min_width = 1159,
                    column_width = 59
                ),
                self._create(
                    GridSize,
                    identifier = "M",
                    min_width = 929,
                    column_width = 60
                ),
                self._create(
                    GridSize,
                    identifier = "S",
                    min_width = 713,
                    column_width = 42
                ),
                self._create(
                    GridSize,
                    identifier = "XS",
                    min_width = 0,
                    column_width = 32,
                    column_spacing = 8
                )
            ]
        )

    def create_controllers(self):
        for controller_name in (
            "Publishable",
            "File",
            "URI",
            "Styles",
            "FirstChildRedirection",
            "Login",
            "PasswordChange",
            "PasswordChangeConfirmation"
        ):
            controller = self._create(
                Controller,
                qname = "woost.%s_controller" % controller_name.lower(),
                title = TranslatedValues(),
                python_name = "woost.controllers.%scontroller.%sController" % (
                    controller_name.lower(),
                    controller_name
                )
            )
            setattr(self, controller_name.lower() + "_controller", controller)

        # Setup default controllers
        self.configuration.default_publishable_controller = (
            Controller.require_instance(
                qname = "woost.publishable_controller"
            )
        )
        self.configuration.default_file_controller = (
            Controller.require_instance(
                qname = "woost.file_controller"
            )
        )
        self.configuration.default_uri_controller = (
            Controller.require_instance(
                qname = "woost.uri_controller"
            )
        )

    def create_default_page_template(self):
        return self._create(
            Template,
            qname = "woost.default_page_template",
            title = TranslatedValues(),
            identifier = "woost.views.GenericSiteLayout",
        )

    def create_default_news_template(self):
        return self._create(
            Template,
            qname = "woost.default_news_template",
            title = TranslatedValues(),
            identifier = "woost.views.GenericSiteLayout",
        )

    def create_default_event_template(self):
        return self._create(
            Template,
            qname = "woost.default_event_template",
            title = TranslatedValues(),
            identifier = "woost.views.GenericSiteLayout",
        )

    def create_home(self):
        return self._create(
            Page,
            title = TranslatedValues("home.title"),
            inner_title = TranslatedValues("home.inner_title"),
            blocks = [
                self._create(
                    TextBlock,
                    text = TranslatedValues("home.body")
                )
            ]
        )

    def create_user_stylesheet(self):
        return self._create(
            Document,
            qname = "woost.user_styles",
            title = TranslatedValues(),
            per_language_publication = False,
            controller = self.styles_controller,
            path = "user_styles",
            hidden = True,
            mime_type = "text/css",
            caching_policies = [
                self._create(
                    CachingPolicy,
                    cache_tags_expression =
                        "tags.add('woost.models.style.Style')\n",
                    server_side_cache = True
                )
            ]
        )

    def create_generic_error_page(self):
        return self._create(
            Page,
            qname = "woost.generic_error_page",
            title = TranslatedValues(),
            hidden = True,
            blocks = [
                self._create(
                    TextBlock,
                    text = TranslatedValues("generic_error_page.body"),
                    initialization =
                        "from woost.models import Configuration\n"
                        "setting = Configuration.instance.get_setting\n"
                        "email = setting('technical_contact_email') or setting('email')\n"
                        "if email:\n"
                        "    repl = '(<a href=\"mailto:' + email + '\">' + email + '</a>)'\n"
                        "else:\n"
                        "    repl = ''\n"
                        "view.text = view.text.replace('[CONTACT]', repl)"
                ),
                self._create(
                    CustomBlock,
                    view_class = "woost.views.Traceback"
                )
            ]
        )

    def create_not_found_error_page(self):
        return self._create(
            Page,
            qname = "woost.not_found_error_page",
            title = TranslatedValues(),
            hidden = True,
            blocks = [
                self._create(
                    TextBlock,
                    text = TranslatedValues("not_found_error_page.body")
                )
            ]
        )

    def create_forbidden_error_page(self):
        return self._create(
            Page,
            qname = "woost.forbidden_error_page",
            title = TranslatedValues(),
            hidden = True,
            blocks = [
                self._create(
                    TextBlock,
                    text = TranslatedValues("forbidden_error_page.body")
                )
            ]
        )

    def create_password_change_page(self):
        return self._create(
            Page,
            qname = "woost.password_change_page",
            title = TranslatedValues(),
            controller = self.passwordchange_controller,
            hidden = True,
            blocks = [
                self._create(
                    TextBlock,
                    text = TranslatedValues("password_change_page.body"),
                    initialization =
                        'import cherrypy\n'
                        'if cherrypy.request.method == "POST":\n'
                        '    view.visible = False'
                ),
                self._create(
                    CustomBlock,
                    heading = TranslatedValues("password_change_page.form_title"),
                    view_class = "woost.views.PasswordChangeRequestForm",
                    controller =
                        "woost.controllers.passwordchangecontroller."
                        "PasswordChangeBlockController"
                )
            ]
        )

    def create_password_change_confirmation_page(self):
        return self._create(
            Page,
            qname = "woost.password_change_confirmation_page",
            title = TranslatedValues(),
            controller = self.passwordchangeconfirmation_controller,
            hidden = True,
            blocks = [
                self._create(
                    TextBlock,
                    text = TranslatedValues(
                        "password_change_confirmation_page.body"
                    ),
                    initialization =
                        'import cherrypy\n'
                        'if cherrypy.request.method == "POST":\n'
                        '    view.visible = False'
                ),
                self._create(
                    CustomBlock,
                    heading = TranslatedValues(
                        "password_change_confirmation_page.form_title"
                    ),
                    view_class = "woost.views.PasswordChangeConfirmationForm",
                    controller =
                        "woost.controllers.passwordchangecontroller."
                        "PasswordChangeConfirmationBlockController"
                )
            ]
        )

    def create_password_change_email_template(self):
        return self._create(
            EmailTemplate,
            qname = "woost.password_change_email_template",
            template_engine = "mako",
            title = TranslatedValues(),
            subject = TranslatedValues(),
            body = TranslatedValues(),
            sender = 'u"noreply@' + self.hosts[0] + '"',
            receivers = "[user.email]"
        )

    def create_login_page(self):
        return self._create(
            Page,
            qname = "woost.login_page",
            title = TranslatedValues(),
            hidden = True,
            blocks = [
                self._create(LoginBlock)
            ]
        )

    def create_content_renderer(self):
        return self._create(
            rendering.ChainRenderer,
            qname = "woost.content_renderer",
            title = TranslatedValues(),
            renderers = [
                self._create(rendering.ImageFileRenderer),
                self._create(rendering.PDFRenderer),
                self._create(rendering.VideoFileRenderer),
                self._create(rendering.ImageURIRenderer)
            ]
        )

    def create_icon16_renderer(self):
        return self._create(
            rendering.IconRenderer,
            qname = "woost.icon16_renderer",
            title = TranslatedValues(),
            icon_size = 16
        )

    def create_icon32_renderer(self):
        return self._create(
            rendering.IconRenderer,
            qname = "woost.icon32_renderer",
            title = TranslatedValues(),
            icon_size = 32
        )

    def create_default_image_factory(self):
        return self._create(
            rendering.ImageFactory,
            qname = "woost.default_image_factory",
            title = TranslatedValues(),
            identifier = "default"
        )

    def create_icon16_image_factory(self):
        return self._create(
            rendering.ImageFactory,
            qname = "woost.icon16_image_factory",
            title = TranslatedValues(),
            identifier = "icon16",
            renderer = self.icon16_renderer,
            applicable_to_blocks = False
        )

    def create_icon32_image_factory(self):
        return self._create(
            rendering.ImageFactory,
            qname = "woost.icon32_image_factory",
            title = TranslatedValues(),
            identifier = "icon32",
            renderer = self.icon32_renderer,
            applicable_to_blocks = False
        )

    def create_edit_blocks_thumbnail_image_factory(self):
        return self._create(
            rendering.ImageFactory,
            qname = "woost.edit_blocks_thumbnail_image_factory",
            title = TranslatedValues(),
            identifier = "edit_blocks_thumbnail",
            effects = [
                self._create(
                    rendering.Thumbnail,
                    width = "75",
                    height = "75"
                ),
                self._create(
                    rendering.Frame,
                    edge_width = 1,
                    edge_color = "ccc",
                    vertical_padding = "4",
                    horizontal_padding = "4",
                    background = "eee"
                )
            ],
            applicable_to_blocks = False
        )

    def create_close_up_image_factory(self):
        return self._create(
            rendering.ImageFactory,
            qname = "woost.close_up_image_factory",
            title = TranslatedValues(),
            identifier = "image_gallery_close_up",
            effects = [
                self._create(
                    rendering.Fill,
                    width = "900",
                    height = "700",
                    preserve_vertical_images = True
                )
            ]
        )

    def create_default_thumbnail_image_factory(self):
        return self._create(
            rendering.ImageFactory,
            qname = "woost.default_thumbnail_image_factory",
            title = TranslatedValues(),
            identifier = "image_gallery_thumbnail",
            effects = [
                self._create(
                    rendering.Fill,
                    width = "200",
                    height = "150",
                    preserve_vertical_images = True
                )
            ]
        )

    def create_collage_image_factory(self):
        return self._create(
            rendering.ImageFactory,
            qname = "woost.collage_image_factory",
            title = TranslatedValues(),
            identifier = "collage",
            effects = [
                self._create(
                    rendering.Thumbnail,
                    height = "350",
                    upscale = True
                )
            ]
        )

