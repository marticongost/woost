#-*- coding: utf-8 -*-
u"""

.. moduleauthor::  <Martí Congost <marti.congost@whads.com>
"""
from datetime import datetime
from cocktail.pkgutils import import_object
from cocktail.translations import translations, get_language
from cocktail.schema.expressions import Expression
from woost import app
from .item import Item
from .permission import (
    ReadPermission,
    ReadTranslationPermission,
    PermissionExpression
)


class PublishableObject(object):
    """Abstract mixin class for all classes with instances that can be
    published.
    """
    cacheable = True
    cacheable_server_side = True
    backoffice_card_view = "woost.views.PublishableCard"
    type_group = "publishable"

    any_language = object()
    any_website = object()

    mime_type = "text/html"
    resource_type = "document"
    encoding = "utf-8"
    controller = None
    template = None
    theme = None
    parent = None
    menu_title = None
    path = None
    full_path = None
    hidden = False
    login_page = None
    robots_should_index = True
    per_language_publication = False
    enabled = True
    enabled_translations = ()
    websites = ()
    access_level = None
    start_date = None
    end_date = None
    requires_https = False
    caching_policies = ()
    redirection_mode = None
    redirection_target = None
    redirection_method = None

    def get_controller(self):
        return self.controller or self.get_default_controller()

    def get_default_controller(self):
        return None

    def resolve_controller(self):
        controller = self.get_controller()
        if controller and controller.python_name:
            return import_object(controller.python_name)
        return None

    def get_template(self):
        return self.template or self.get_default_template()

    def get_default_template(self):
        return None

    def get_effective_caching_policy(self, **context):

        from woost.models import Configuration

        policies = [
            ((-policy.important, 1), policy)
            for policy in self.caching_policies
        ]
        policies.extend(
            ((-policy.important, 2), policy)
            for policy in Configuration.instance.caching_policies
        )
        policies.sort()

        for criteria, policy in policies:
            if policy.applies_to(self, **context):
                return policy

    def get_ancestor(self, depth):
        """Obtain one of the item's ancestors, given its depth in the document
        tree.

        @param depth: The depth level of the ancestor to obtain, with 0
            indicating the root of the tree. Negative indices are accepted, and
            they reverse the traversal order (-1 will point to the item itself,
            -2 to its parent, and so on).
        @type depth: int

        @return: The requested ancestor, or None if there is no ancestor with
            the indicated depth.
        @rtype: L{PublishableObject}
        """
        tree_line = list(self.ascend_tree(include_self = True))
        tree_line.reverse()
        try:
            return tree_line[depth]
        except IndexError:
            return None

    def ascend_tree(self, include_self = False):
        """Iterate over the item's ancestors, moving towards the root of the
        document tree.

        @param include_self: Indicates if the object itself should be included
            in the iteration.
        @type include_self: bool

        @return: An iterable sequence of pages.
        @rtype: L{Document} iterable sequence
        """
        publishable = self if include_self else self.parent
        while publishable is not None:
            yield publishable
            publishable = publishable.parent

    def descend_tree(self, include_self = False):
        """Iterate over the item's descendants.

        @param include_self: Indicates if the object itself should be included
            in the iteration.
        @type include_self: bool

        @return: An iterable sequence of publishable elements.
        @rtype: L{PublishableObject} iterable sequence
        """
        if include_self:
            yield self

    def descends_from(self, page):
        """Indicates if the object descends from the given document.

        @param page: The hypothetical ancestor of the page.
        @type page: L{Document<woost.models.document.Document>}

        @return: True if the object is contained inside the given document or
            one of its descendants, or if it *is* the given document. False in
            any other case.
        @rtype: bool
        """
        ancestor = self

        while ancestor is not None:
            if ancestor is page:
                return True
            ancestor = ancestor.parent

        return False

    def is_home_page(self):
        """Indicates if the object is the home page for any website.
        @rtype: bool
        """
        return False

    def is_internal_content(self, language = None):
        """Indicates if the object represents content from this site.
        @rtype: bool
        """
        return True

    def is_current(self):
        now = datetime.now()
        return (self.start_date is None or self.start_date <= now) \
            and (self.end_date is None or self.end_date > now)

    def is_published(
        self,
        language = None,
        website = None,
        _user = None
    ):
        from woost.models import Configuration, Website

        if self.per_language_publication:

            target_websites = resolve_websites(website, self)
            if not target_websites:
                return False

            target_languages = resolve_languages(
                language,
                target_websites,
                self,
                _user
            )
            if not target_languages:
                return False
        else:
            if not self.enabled:
                return False

            if website is not PublishableObject.any_website:
                target_websites = resolve_websites(website, self)
                if not target_websites:
                    return False

        if not self.is_current():
            return False

        return True

    def is_accessible(self, user = None, language = None, website = None):

        if user is None:
            user = app.user

        return (
            self.is_published(
                language = language,
                website = website,
                _user = user
            )
            and user.has_permission(
                ReadPermission,
                target = self
            )
        )

    @classmethod
    def select_published(cls, *args, **kwargs):

        language = kwargs.pop("language", None)
        website = kwargs.pop("website", None)

        query = cls.select(*args, **kwargs)
        query.add_filter(
            cls.IsPublishedExpression(
                language = language,
                website = website
            )
        )
        return query

    @classmethod
    def select_accessible(cls, *args, **kwargs):

        user = kwargs.pop("user", None)
        language = kwargs.pop("language", None)
        website = kwargs.pop("website", None)

        query = cls.select(*args, **kwargs)
        query.add_filter(
            cls.IsAccessibleExpression(
                user = user,
                language = language,
                website = website
            )
        )
        return query

    def get_uri(self, **kwargs):
        return app.url_mapping.get_url(self, **kwargs)

    def translate_file_type(self, language = None):

        trans = ""

        mime_type = self.mime_type
        if mime_type:
            trans = translations("woost.mime." + mime_type, language = language)

        if not trans:

            res_type = self.resource_type
            if res_type:
                trans = self.__class__.resource_type.translate_value(
                    res_type,
                    language = language
                )

                if trans and res_type != "other":
                    ext = self.file_extension
                    if ext:
                        trans += " " + ext.upper().lstrip(".")

        return trans

    def get_cache_expiration(self):
        now = datetime.now()

        start = self.start_date
        if start is not None and start > now:
            return start

        end = self.end_date
        if end is not None and end > now:
            return end

    class IsPublishedExpression(Expression):
        """An expression that tests if items are published."""

        def __init__(
            self,
            language = None,
            website = None,
            _user = None
        ):
            Expression.__init__(self, language, website)
            self.language = language
            self.website = website
            self._user = None

        def eval(self, context, accessor = None):
            return context.is_published(
                language = self.language,
                website = self.website,
                _user = self._user
            )

    class IsAccessibleExpression(Expression):
        """An expression that tests that items can be accessed by a user.

        The expression checks both the publication state of the item and the
        read permissions for the specified user.

        @ivar user: The user that accesses the items.
        @type user: L{User<woost.models.user.User>}
        """

        def __init__(self, user = None, language = None, website = None):
            Expression.__init__(self)
            self.user = user
            self.language = language
            self.website = website

        def eval(self, context, accessor = None):
            return context.is_accessible(
                language = self.language,
                website = self.website,
                user = self.user
            )

        def iter_filter_expressions(self, query):
            user = self.user or app.user
            yield PermissionExpression(user, ReadPermission)
            yield query.type.IsPublishedExpression(
                language = self.language,
                website = self.website,
                _user = user
            )


mime_type_categories = {}

for category, mime_types in (
    ("text/plain", ("text",)),
    ("html_resource", (
        "text/css",
        "text/javascript",
        "text/ecmascript",
        "application/javascript",
        "application/ecmascript"
    )),
    ("document", (
        "application/vnd.oasis.opendocument.text",
        "application/vnd.oasis.opendocument.spreadsheet",
        "application/vnd.oasis.opendocument.presentation",
        "application/msword",
        "application/msexcel",
        "application/msaccess",
        "application/mspowerpoint",
        "application/mswrite",
        "application/vnd.ms-excel",
        "application/vnd.ms-access",
        "application/vnd.ms-powerpoint",
        "application/vnd.ms-project",
        "application/vnd.ms-works",
        "application/vnd.ms-xpsdocument",
        "application/rtf",
        "application/pdf",
        "application/x-pdf",
        "application/postscript",
        "application/x-latex",
        "application/vnd.oasis.opendocument.database"
    )),
    ("package", (
        "application/zip",
        "application/x-rar-compressed",
        "application/x-tar",
        "application/x-gtar",
        "application/x-gzip",
        "application/x-bzip",
        "application/x-stuffit",
        "vnd.ms-cab-compressed"
    ))
):
    for mime_type in mime_types:
        mime_type_categories[mime_type] = category

def get_category_from_mime_type(mime_type):
    """Obtains the file category that best matches the indicated MIME type.

    @param mime_type: The MIME type to get the category for.
    @type mime_type: str

    @return: A string identifier with the category matching the indicated
        MIME type (one of 'document', 'image', 'audio', 'video', 'package',
        'html_resource' or 'other').
    @rtype: str
    """
    pos = mime_type.find("/")

    if pos != -1:
        prefix = mime_type[:pos]

        if prefix in ("image", "audio", "video"):
            return prefix

    return mime_type_categories.get(mime_type, "other")


def resolve_websites(website, publishable = None):

    from woost.models import Configuration, Website

    website = website or app.website or PublishableObject.any_website

    if website is PublishableObject.any_website:
        websites = set(Configuration.instance.websites)
    elif isinstance(website, Website):
        websites = {website,}
    else:
        websites = website

    if publishable is not None:
        publishable_websites = publishable.websites
        if publishable_websites:
            websites.intersection_update(publishable_websites)

    return websites

def resolve_languages(
    language,
    websites,
    publishable = None,
    user = None
):
    language = language or get_language() or PublishableObject.any_language

    website_languages = set()
    for website in websites:
        website_languages.update(website.get_published_languages())

    if language is PublishableObject.any_language:
        languages = website_languages
    elif isinstance(language, basestring):
        if language in website_languages:
            languages = {language}
        else:
            return set()
    else:
        languages = website_languages.intersection(language)

    if publishable is not None and publishable.per_language_publication:
        languages.intersection_update(publishable.enabled_translations)

    if user is not None:
        languages = {
            language
            for language in languages
            if user.has_permission(
                ReadTranslationPermission,
                language = language
            )
        }

    return languages

def get_publishable(id):
    obj = Item.get_instance(id)
    if obj and isinstance(obj, PublishableObject):
        return obj
    else:
        return None

publishable_full_path_resolvers = []

def get_publishable_by_full_path(full_path):

    for resolver in publishable_full_path_resolvers:
        publishable = resolver(full_path)
        if publishable is not None:
            return publishable

    return None

