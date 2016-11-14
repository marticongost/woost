#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from xml.sax.saxutils import escape, quoteattr
from cocktail import schema
from woost import app
from woost.models import Publishable, LocaleMember, Controller


class SiteMap(Publishable):

    type_group = "resource"

    default_hidden = True
    default_per_language_publication = False

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(
            qname = "woost.extensions.sitemap.sitemap_controller"
        )
    )

    members_order = [
        "title",
        "included_locales",
        "content_expression",
        "entries_expression"
    ]

    title = schema.String(
        translated = True,
        descriptive = True
    )

    included_locales = schema.Collection(
        items = LocaleMember(),
        edit_control = "cocktail.html.SplitSelector",
        default_type = set
    )

    content_expression = schema.CodeBlock(
        language = "python"
    )

    entries_expression = schema.CodeBlock(
        language = "python"
    )

    def iter_entries(self):

        language_subset = app.website.get_published_languages(
            languages = self.included_locales or None
        )

        content = Publishable.select_accessible(
            Publishable.robots_should_index.equal(True),
            language = language_subset
        )

        if self.content_expression:
            context = {
                "site_map": self,
                "content": content
            }
            SiteMap.content_expression.execute(self, context)
            content = context["content"]

        for publishable in content:

            if not publishable.is_internal_content():
                continue

            if publishable.per_language_publication:
                languages = language_subset & publishable.enabled_translations
            else:
                languages = ("x-default",)

            if not languages:
                continue

            properties = {}

            if publishable.sitemap_priority:
                properties["priority"] = publishable.sitemap_priority

            if publishable.sitemap_change_frequency:
                properties["changefreq"] = publishable.sitemap_change_frequency

            entries = [
                (
                    properties,
                    [
                        (
                            language,
                            publishable.get_uri(
                                host = "!",
                                language = language
                            )
                        )
                        for language in languages
                    ]
                )
            ]

            if self.entries_expression:
                context = {
                    "site_map": self,
                    "publishable": publishable,
                    "languages": languages,
                    "entries": entries,
                    "default_properties": properties
                }
                SiteMap.entries_expression.execute(self, context)
                entries = context["entries"]

            for entry in entries:
                yield entry

    def generate_sitemap(self):

        indent = " " * 4

        yield '<?xml version="1.0" encoding="utf-8"?>\n'
        yield '<urlset\n'
        yield indent
        yield 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        yield indent
        yield 'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'

        for properties, urls in self.iter_entries():

            yield indent
            yield '<url>\n'

            # Main URL
            yield indent * 2
            yield '<loc>%s</loc>\n' % escape(str(urls[0][1]))

            # Properties (priority, change frequency, etc)
            for key, value in properties.iteritems():
                yield indent * 2
                yield '<%s>%s</%s>\n' % (key, escape(str(value)), key)

            # Alternate languages
            if len(urls) > 1:
                for language, url in urls:
                    yield indent * 2
                    yield (
                        '<xhtml:link rel="alternate" '
                        'hreflang=%s '
                        'href=%s/>\n'
                        % (quoteattr(language), quoteattr(str(url)))
                    )

            yield indent
            yield '</url>\n'

        yield '</urlset>\n'

