#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from simplejson import dumps
import cherrypy
from cocktail.translations import translations
from woost.models import Configuration
from woost.controllers.filecontroller import FileController
from woost.controllers.uricontroller import URIController


class GAEventRedirection(object):

    delay = 300

    overridable_category = True
    overridable_action = True
    overridable_label = True

    default_category = None
    default_action = "open"

    template = """
        <!DOCTYPE html>
        <html>
            <head>
                <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
                <title>%(title)s</title>
                <script type="text/javascript">
                    var _gaq = _gaq || [];
                    _gaq.push(['_setAccount', %(account)s]);
                    _gaq.push(['_trackEvent', %(category)s, %(action)s, %(label)s]);
                    window.onload = function () {
                        setTimeout(function () {
                            location.replace(%(url)s);
                        }, %(delay)d);
                    }
                </script>
                <script type="text/javascript" src="http://www.google-analytics.com/ga.js"></script>
            </head>
            <body>
                %(body)s
            </body>
        </html>
        """

    def __init__(self, controller_class):

        base_impl = controller_class.__call__

        def __call__(controller, **kwargs):

            publishable = controller.context["publishable"]

            if self.event_tracking_is_enabled(controller, publishable):
                url = self.get_url(controller, publishable)
                cherrypy.response.headers["Content-Type"] = "text/html"

                return self.template % {
                    "title": self.get_title(controller, publishable),
                    "account": dumps(self.get_account(controller, publishable)),
                    "category": dumps(self.get_category(controller, publishable)),
                    "action": dumps(self.get_action(controller, publishable)),
                    "label": dumps(self.get_label(controller, publishable)),
                    "url": dumps(url),
                    "delay": self.delay,
                    "body": self.get_body(controller, publishable, url = url)
                }

            # Google Analytics event tracking disabled
            else:
                return base_impl(controller, **kwargs)

        controller_class.__call__ = __call__
        controller_class.ga_event_redirection = self

    def event_tracking_is_enabled(self, controller, publishable):
        return cherrypy.request.params.get("ga_event") == "1"

    def get_url(self, controller, publishable):

        extra_params = dict(
            (key, value)
            for key, value in cherrypy.request.params.iteritems()
            if not key.startswith("ga_event")
        )

        return publishable.get_uri(parameters = extra_params)

    def get_account(self, controller, publishable):
        return Configuration.instance.get_setting("google_analytics_account")

    def get_title(self, controller, publishable):
        return translations("woost.extensions.googleanalytics.redirection_title")

    def get_body(self, controller, publishable, url):
        return translations(
            "woost.extensions.googleanalytics.redirection_body",
            url = url
        )

    def get_category(self, controller, publishable):
        return (
            self.overridable_category
            and cherrypy.request.params.get("ga_event_category")
            or self.default_category
            or publishable.__class__.__name__
        )

    def get_action(self, controller, publishable):
        return (
            self.overridable_action
            and cherrypy.request.params.get("ga_event_action")
            or self.default_action
        )

    def get_label(self, controller, publishable):
        return (
            self.overridable_label
            and cherrypy.request.params.get("ga_event_label")
            or str(publishable.id)
        )

GAEventRedirection(FileController)
GAEventRedirection(URIController)

