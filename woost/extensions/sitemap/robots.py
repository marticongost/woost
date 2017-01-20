#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from woost import app
from woost.controllers.robotscontroller import RobotsController, EVERYTHING
from .sitemap import SiteMap


@when(RobotsController.after_default_record_written)
def add_sitemap_directives_to_robots_txt(e):
    first = True
    if e.disallowed_content is not EVERYTHING:
        for sitemap in SiteMap.select_accessible():
            if first:
                e.file.write("\n")
                first = False
            e.file.write("Sitemap: %s\n" % str(sitemap.get_uri(host = "!")))

