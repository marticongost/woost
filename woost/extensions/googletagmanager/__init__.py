#-*- coding: utf-8 -*-
"""

@author:	Martí Congost
@contact:	marti.congost@whads.com
@organization:	Whads/Accent SL
@since:		April 2016
"""
from cocktail.translations import translations
from woost.models import (
    Extension,
    Configuration
)

translations.load_bundle("woost.extensions.googletagmanager.package")


class GoogleTagManagerExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Integra el lloc web amb Google Tag Manager.""",
            "ca"
        )
        self.set("description",
            u"""Integra el sitio web con Google Tag Manager.""",
            "es"
        )
        self.set("description",
            u"""Integrates the site with Google Tag Manager.""",
            "en"
        )

    def _load(self):

        from woost.extensions.googletagmanager import (
            configuration,
            website
        )

        from cocktail.events import when
        from woost.controllers.cmscontroller import CMSController

        @when(CMSController.producing_output)
        def handle_producing_output(e):
            html = e.output.get("body_beginning_html", "")
            if html:
                html += " "
            ext = GoogleTagManagerExtension.instance
            html += ext.get_google_tag_manager_markup()
            e.output["body_beginning_html"] = html

    def get_google_tag_manager_markup(self):
        account_id = \
            Configuration.instance.get_setting("google_tag_manager_account")

        if not account_id:
            return ""
        else:
            return """
                <!-- Google Tag Manager -->
                <noscript><iframe src="//www.googletagmanager.com/ns.html?id=%(account_id)s"
                height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
                <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
                new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
                j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
                '//www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
                })(window,document,'script','dataLayer','%(account_id)s');</script>
                <!-- End Google Tag Manager -->
                """ % {"account_id": account_id}

