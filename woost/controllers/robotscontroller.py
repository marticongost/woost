#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cStringIO import StringIO
from cocktail.events import Event
from cocktail.controllers import Controller, serve_file, request_property
from woost.models import Configuration, Publishable

EVERYTHING = object()


class RobotsController(Controller):

    selecting_disallowed_content = Event()
    selecting_disallowed_uris = Event()
    writing_default_record = Event()
    after_default_record_written = Event()

    def __call__(self, **kwargs):

        # Select publishable elements to disallow
        if Configuration.instance.get_setting("robots_should_index"):
            e = self.selecting_disallowed_content(
                disallowed_content = self.disallowed_content
            )
            disallowed_content = e.disallowed_content
        else:
            disallowed_content = EVERYTHING

        # Create the file
        file = StringIO()
        file.write("User-Agent: *\n")

        if disallowed_content is EVERYTHING:
            file.write("Disallow: /\n")
        else:
            empty = True

            for publishable in disallowed_content:
                for uri in self.get_disallowed_uris(publishable):
                    file.write("Disallow: %s\n" % str(uri))
                    empty = False

            if empty:
                file.write("Disallow:\n")

        e = self.writing_default_record(
            file = file,
            disallowed_content = disallowed_content
        )
        file = e.file

        e = self.after_default_record_written(
            file = file,
            disallowed_content = disallowed_content
        )
        file = e.file

        # Serve the file
        file.seek(0)
        return serve_file(file, content_type = "text/plain")

    @request_property
    def disallowed_content(self):
        return Publishable.select_accessible(
            Publishable.robots_should_index.equal(False),
            language = Publishable.any_language
        )

    def get_disallowed_uris(self, publishable):

        uris = []

        if publishable.per_language_publication:
            for language in publishable.enabled_translations:
                uri = publishable.get_uri(language = language)
                uris.append(uri)
        else:
            uri = publishable.get_uri()
            uris.append(uri)

        e = self.selecting_disallowed_uris(
            publishable = publishable,
            uris = uris
        )
        return e.uris

