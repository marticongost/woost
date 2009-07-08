#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2009
"""
import __builtin__
from datetime import datetime
import cherrypy
from cocktail.controllers.location import Location
from cocktail.translations import translations, set_language
from cocktail.language import set_content_language
from sitebasis.models import Feed, DocumentIsAccessibleExpression
from sitebasis.controllers.basecmscontroller import BaseCMSController


class FeedsController(BaseCMSController):

    def __call__(self, feed_id, language):

        feed = None

        if feed_id and language and language:
            try:
                feed_id = int(feed_id)
            except:
                pass

            feed = Feed.get_instance(feed_id)

        if feed is None \
        or not feed.enabled \
        or language not in feed.translations:
            raise cherrypy.NotFound()

        set_language(language)
        set_content_language(language)
        cms = self.context["cms"]
        location = Location.get_current()
        location.relative = False

        def rfc822_date(date):
            return date.strftime("%d %%s %Y %H:%M:%S %Z") % [
                "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
            ][date.month]

        params = {
            "title": feed.title,
            "url": unicode(location),
            "description": feed.description,
            "language": language,
            "now": rfc822_date(datetime.now())
        }

        location.path_info = self.application_uri()
        location.query_string = None
        base_url = unicode(location)
        params["base_url"] = base_url
        
        cherrypy.response.headers["Content-Type"] = \
            "application/rss+xml;charset=utf-8"

        output = []
        output.append(u"""<?xml version='1.0' encoding='utf-8'?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title><![CDATA[%(title)s]]></title>
        <link><![CDATA[%(base_url)s]]></link>
        <description><![CDATA[%(description)s]]></description>
        <language>%(language)s</language>
        <pubDate>%(now)s</pubDate>
        <atom:link href="%(url)s" rel="self" type="application/rss+xml" />
""" % params)
        
        if feed.image:
            image_uri = feed.image.uri
            
            if image_uri.startswith("/"):
                image_uri = base_url + image_uri[1:]

            params["image_url"] = image_uri
            output.append(u"""
        <image>
            <url>%(image_url)s</url>
            <title>%(title)s</title>
            <link>%(base_url)s</link>
        </image>""" % params)

        if feed.ttl:
            output.append(u"""
        <ttl>%d</ttl>""" % feed.ttl)

        context = {
            "__builtins__": __builtin__,
            "feed": feed,
            "language": language,
            "canonical_uri": cms.canonical_uri,
            "translations": translations
        }

        items = feed.select_items()
       
        for item in items:
            context["item"] = item
            
            title = eval(feed.item_title_expression, context)            
            if not title:
                continue

            link = eval(feed.item_link_expression, context)
            if not link:
                continue

            if link.startswith("/"):                
                link = base_url + link[1:]
            
            output.append(
u"""        <item>
            <title><![CDATA[%(title)s]]></title>
            <url><![CDATA[%(url)s]]></url>
            <guid isPermaLink="%(perma_link)s"><![CDATA[%(url)s]]></guid>
        """ % {
                "title": title,
                "url": link,
                "perma_link": cms.document_resolver.permanent_links
                    and "true" or "false"
            })
            
            pub_date = eval(feed.item_publication_date_expression, context)
            if pub_date:
                output.append(
u"""            <pubDate><![CDATA[%s]]></pubDate>""" % rfc822_date(pub_date))

            description = eval(feed.item_description_expression, context)
            if description:
                output.append(
u"""            <description><![CDATA[%s]]></description>""" % description)

            output.append(
u"""        </item>""")

        output.append(u"""
    </channel>
</rss>""")
        return u"\n".join(output).encode("utf-8")

