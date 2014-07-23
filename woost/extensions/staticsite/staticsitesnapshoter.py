#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			March 2010
"""
import os
from shutil import rmtree
from subprocess import Popen, PIPE
from cocktail import schema
from cocktail.translations import language_context
from cocktail.controllers import context as controller_context
from cocktail.modeling import abstractmethod, getter
from cocktail.translations import translations
from woost import app
from woost.models import Item


class StaticSiteSnapShoter(Item):
    """A class tasked with creating a static snapshot of a site's content to
    a concrete location.
    
    This is mostly an abstract class, meant to be extended by subclasses. Each
    subclass should implement the static snapshot creation. 
    """
    instantiable = False
    visible_from_root = False
    integral = True

    members_order = [
        "setup_expression",
        "postprocessing_expression"
    ]

    setup_expression = schema.CodeBlock(
        language = "python"
    )

    postprocessing_expression = schema.CodeBlock(
        language = "python"        
    )

    def setup(self, context):
        """Prepares the exporter for an export process.

        The object of this method is to allow exporters to perform any
        initialization they require before writing files to their destination.

        @param context: A dictionary where the exporter can place any
            contextual information it many need throgout the export process. It
            will be made available to all L{write_file} calls.
        @type context: dict
        """
        setup_expression = self.setup_expression
        if setup_expression:
            setup_expression = compile(
                setup_expression,
                "%s #%d.setup_expression" % (self.__class__.__name__, self.id),
                "exec"
            )
            exec setup_expression in context

    def cleanup(self, context):
        """Frees resources after an export operation.

        This method is guaranteed to be called after the export operation is
        over, even if an exception was raised during its execution.

        @param context: The dictionary used by the exporter during the export
            process to maintain its contextual information.
        @type context: dict
        """

    def snapshot(self, items, context = None):
        """ Generates the snapshot of a site's content 

        @param items: The list of items which the exportation will start.
        @type items: L{Publishable}

        @param context: A dictionary used to share any contextual information
            with the snapshoter.
        @type context: dict
        """
        if context is None:
            context = {}

        self.setup(context)

        try:
            return self._snapshot(items, context)
        finally:
            self.cleanup(context)

    @abstractmethod
    def _snapshot(self, items, context):
        """ Generates the snapshot of a site's content 

        @param items: The list of items which the exportation will start.
        @type items: L{Publishable}

        @param context: A dictionary used to share any contextual information
            with the snapshoter.
        @type context: dict
        """

    def _yield_directory(self, directory, context):

        postprocessing = self.postprocessing_expression
        if postprocessing:
            postprocessing = compile(
                postprocessing,
                "%s #%d.postprocessing_expression" % (
                    self.__class__.__name__,
                    self.id
                ),
                "exec"
            )

        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)

                if isinstance(file_path, str):
                    file_path = file_path.decode("utf-8")

                relative_path = os.path.relpath(file_path, directory)

                if postprocessing is not None:
                    exec_context = context.copy()
                    exec_context["file_path"] = file_path
                    exec_context["relative_path"] = relative_path
                    exec postprocessing in exec_context

                yield (file_path, relative_path)


class WgetSnapShoter(StaticSiteSnapShoter):
    """ A class that creates a static snapshot of a site's content using wget """
    instantiable = True

    file_names_mode = schema.String(                                          
        required = True,
        default = "unix",
        text_search = False,
        enumeration = frozenset(("unix", "windows")),
        translate_value = lambda value, **kwargs:    
            u"" if not value else translations(
                "woost.extensions.staticsite.staticsitesnapshoter.WgetSnapShoter.file_names_mode " + value,
                **kwargs
            )
    )

    @getter
    def snapshot_path(self):
        return app.path("snapshots", str(self.id))

    def _get_cmd(self, context):
        cmd = "wget "

        if context.get("follow_links"):
            cmd += " --mirror"

        cmd += (
            " --header='X-Woost-StaticSiteSnapshoter: " + self.__class__.__name__ + "'"
            " --page-requisites"
            " --html-extension"
            " --convert-links"
            " --no-host-directories"
            " --no-check-certificate"
            " --trust-server-names"
            " --directory-prefix=%s"
            " --restrict-file-names=%s %s"
        )

        return cmd

    def _snapshot(self, items, context = {}):

        cmd = self._get_cmd(context)
        uris = set()

        for item in items:
            if isinstance(item, basestring):
                uris.add(item)
            else:
                if item.per_language_publication:
                    for language in item.enabled_translations:
                        with language_context(language):
                            uris.add(self._get_uri(item, context))
                else:
                    uris.add(self._get_uri(item, context))

        cmd = cmd % (
            self.snapshot_path, 
            self.file_names_mode, 
            u" ".join(uris)
        )

        p = Popen(cmd, shell=True, stdout=PIPE)
        p.communicate()

        for item in self._yield_directory(self.snapshot_path, context):
            yield item

    def _get_uri(self, item, context):
        uri = item.get_uri(host = "!")
        if isinstance(uri, unicode):
            uri = uri.encode("utf-8")
        return uri

    def cleanup(self, context):
        if os.path.exists(self.snapshot_path):
            rmtree(self.snapshot_path)

