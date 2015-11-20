#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2009
"""
from simplejson import dumps
from cocktail.translations import translations, get_language
from cocktail.events import Event
from cocktail.controllers import context
from woost import app
from woost.models import (
    Extension,
    Configuration
)

translations.define("GoogleAnalyticsExtension",
    ca = u"Google Analytics",
    es = u"Google Analytics",
    en = u"Google Analytics"
)

translations.define("GoogleAnalyticsExtension-plural",
    ca = u"Google Analytics",
    es = u"Google Analytics",
    en = u"Google Analytics"
)

translations.define("GoogleAnalyticsExtension.account",
    ca = u"Compte",
    es = u"Cuenta",
    en = u"Account"
)


class GoogleAnalyticsExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Integra el lloc web amb Google Analytics.""",
            "ca"
        )
        self.set("description",
            u"""Integra el sitio web con Google Analytics.""",
            "es"
        )
        self.set("description",
            u"""Integrates the site with Google Analytics.""",
            "en"
        )

    def _load(self):

        from woost.extensions.googleanalytics import (
            strings,
            configuration,
            website,
            document,
            textblock,
            eventredirection
        )

        # Install an overlay for text blocks to automatically generate events
        # when their block link is clicked
        from cocktail.html import templates
        templates.get_class(
            "woost.extensions.googleanalytics.TextBlockViewOverlay"
        )

        from cocktail.events import when
        from woost.controllers import CMSController

        @when(CMSController.producing_output)
        def handle_producing_output(e):
            publishable = e.output.get("publishable")
            if (
                publishable is None
                or getattr(publishable, "is_ga_tracking_enabled", lambda: True)()
            ):
                html = e.output.get("head_end_html", "")
                if html:
                    html += " "
                html += self.get_analytics_page_hit_script(publishable)
                e.output["head_end_html"] = html

    inclusion_code = {
        "async":
            """
            <script type="text/javascript">
              (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
              (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
              m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
              })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
              %(create_tracker_command)s
              %(commands)s
            </script>
            """,
        "sync":
            """
            <script type="text/javascript">
              (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
              (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
              m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
              })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
              %(create_tracker_command)s;
              ga(function () {
                  %(commands)s
              });
            </script>
            """,
    }

    declaring_tracker = Event()

    def get_analytics_script(self,
        publishable = None,
        commands = None,
        async = True
    ):
        config = Configuration.instance

        if publishable is None:
            publishable = app.publishable

        event = self.declaring_tracker(
            publishable = publishable,
            account = config.get_setting("google_analytics_account"),
            tracker_parameters = {},
            domain = config.get_setting("google_analytics_domain"),
            template =
                self.inclusion_code["async" if async else "sync"],
            values = self.get_analytics_values(publishable),
            commands = commands or []
        )

        if not event.account:
            return ""

        commands = event.commands
        parameters = {}

        if event.domain:
            event.tracker_parameters["cookieDomain"] = event.domain

        parameters["create_tracker_command"] = \
            self._serialize_commands([(
                "create",
                event.account,
                event.tracker_parameters
            )])

        if event.values:
            commands.insert(0, ("set", event.values))

        parameters["commands"] = self._serialize_commands(commands)
        return event.template % parameters

    def get_analytics_page_hit_script(self, publishable = None):
        return self.get_analytics_script(
            publishable = publishable,
            commands = [("send", "pageview")]
        )

    def get_analytics_values(self, publishable):
        return {
            # Custom dimension: language
            "dimension1": get_language() or "",

            # Custom dimension: roles
            "dimension2":
                self._serialize_collection(
                    role.id for role in app.user.iter_roles()
                ),

            # Custom dimension: path
            "dimension3":
                "" if publishable is None
                else self._serialize_collection(
                    ancestor.id
                    for ancestor
                    in reversed(list(publishable.ascend_tree(True)))
                )
        }

    def _serialize_collection(self, value):
        return "-" + "-".join(str(item) for item in value) + "-"

    def _serialize_commands(self, commands):
        return "\n".join(
            "ga(%s);" % (", ".join(dumps(arg) for arg in cmd))
            for cmd in commands
        )

