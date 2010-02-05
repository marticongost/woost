#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
from __future__ import with_statement
import os
from shutil import copy
from hashlib import md5
from cStringIO import StringIO
import ftplib
import cherrypy
from cocktail.events import EventHub, Event
from cocktail import schema
from cocktail.modeling import abstractmethod, SetWrapper
from cocktail.language import content_language_context
from cocktail.translations import translations, language_context
from cocktail.persistence import PersistentMapping
from cocktail.controllers import context as controller_context
from woost.models import Item, Publishable, File, Site


class StaticSiteExporter(Item):
    """A class tasked with publishing a static snapshot of a site's content to
    a concrete location.
    
    This is mostly an abstract class, meant to be extended by subclasses. Each
    subclass should implement exporting to a concrete kind of location or
    media. Subclasses must implement L{write_file} and L{create_folder}, and
    probably L{setup}.

    @var chunk_size: The number of bytes written at once by L{write_file}.
    @type chunk_size: int
    """
    instantiable = False
    visible_from_root = False
    chunk_size = 1024 * 8

    def __init__(self, *args, **kwargs):
        Item.__init__(self, *args, **kwargs)
        self.__last_export_hashes = PersistentMapping()

    def setup(self, context):
        """Prepares the exporter for an export process.

        The object of this method is to allow exporters to perform any
        initialization they require before writing files to their destination.

        @param context: A dictionary where the exporter can place any
            contextual information it many need throgout the export process. It
            will be made available to all L{write_file} calls.
        @type context: dict
        """
    
    def cleanup(self, context):
        """Frees resources after an export operation.

        This method is guaranteed to be called after the export operation is
        over, even if an exception was raised during its execution.

        @param context: The dictionary used by the exporter during the export
            process to maintain its contextual information.
        @type context: dict
        """

    def has_changes(self, publishable):
        """Indicates if the given item has pending changes that haven't been
        exported.

        @param publishable: The publishable item to evaluate.
        @type publishable: L{Publishable<woost.models.publishable.Publishable>}

        @return: True if the item was modified after the last time it was
            exported to this destination.
        @rtype: bool
        """
        file, hash = self._get_item_contents(publishable)
        return hash != self.__last_export_hashes.get(publishable.id)

    def export(self,
        selection = None,
        languages = None,
        update_only = False,
        status_tracker = None):
        """Exports site content to this destination.

        @param selection: If specified, only the given subset of publishable
            items will be exported. Regardless of this parameter, items that
            are not published or whose X{exportable_as_static_content} member
            is set to False will never be exported.
        @type selection: L{Publishable<woost.models.publishable.Publishable>}
            sequence

        @param languages: Specifies a subset of translations to export. If not
            specified, items are exported into all of their translations.
        @type languages: str sequence

        @param update_only: When set to True, items will only be exported if
            they have pending changes that have not been exported to this
            destination yet.
        @type update_only: bool

        @param status_tracker: An object to report events to during the export
            process.
        @type status_tracker: L{StatusTracker}
        """
        controller_context["exporting_static_site"] = True

        try:
            context = {"existing_folders": set()}
            self.setup(context)

            if selection is None:
                selection = Publishable.select()
            
            if languages is not None \
            and not isinstance(languages, (set, frozenset, SetWrapper)):
                languages = set(languages)

            if status_tracker:
                status_tracker.beginning(
                    selection = selection,
                    languages = languages,
                    context = context
                )

            for item in selection:

                # Ignored items
                if not item.exportable_as_static_content \
                or not item.is_published():
                    if status_tracker:
                        status_tracker.item_processed(
                            publishable = item,
                            language = None,
                            status = "ignored",
                            context = context,
                            error = None,
                            error_handled = False
                        )
                else:
                    # Determine the languages to export
                    if item.per_language_publication:                        
                        if languages:
                            item_languages = \
                                languages.intersection(item.translations)
                        else:
                            item_languages = item.translations
                    else:
                        item_languages = (None,)
                    
                    for language in item_languages:
                        try:
                            self.export_item(
                                item,
                                context,
                                language = language,
                                update_only = update_only
                            )
                        except Exception, error:

                            handled = False

                            if status_tracker:
                                e = status_tracker.item_processed(
                                    publishable = item,
                                    language = language,
                                    status = "failed",
                                    context = context,
                                    error = error,
                                    error_handled = False
                                )
                                handled = e.error_handled

                            if not handled:
                                raise

                        else:
                            if status_tracker:
                                status_tracker.item_processed(
                                    publishable = item,
                                    language = language,
                                    status = "exported",
                                    context = context,
                                    error = None,
                                    error_handled = False
                                )
        finally:
            del controller_context["exporting_static_site"]
            self.cleanup(context)

    def export_item(self,
        publishable,
        context,
        language = None,
        update_only = False):
        """Exports a publishable item.
        
        @param publishable: The publishable item to export.
        @type publishable: L{Publishable<woost.models.publishable.Publishable>}

        @param language: The language to export the item in.
        @type language: str

        @param update_only: When set to True, the item will only be exported if
            it has pending changes that have not been exported to this
            destination yet.
        @type update_only: bool
        
        @return: True if the item is exported, False if L{update_only} is set
            to True and the item has no changes to export.
        @rtype: bool
        """
        from cocktail.styled import styled
        print styled(publishable, "pink")

        def export():
            file, hash = self._get_item_contents(publishable)

            if update_only \
            and hash == self.__last_export_hashes.get(publishable.id):
                return False
            
            relative_path = Site.main.get_path(publishable, language)

            if language:
                relative_path = os.path.join(language, relative_path)

            print styled(relative_path, "bright_green")
            folder, filename = os.path.split(relative_path)
            if not filename:
                relative_path += "index.html"

            self.create_path(folder, context)
            self.write_file(file, relative_path, context)
            self.__last_export_hashes[publishable.id] = hash
            return True

        if language:
            with language_context(language):
                with content_language_context(language):
                    return export()
        else:
            return export()

    def create_path(self, relative_path, context):
        """Recursively creates all folders in the given path.

        The method will invoke L{create_folder} for each folder in the provided
        path.

        @param relative_path: The path to create, relative to the destination's
            root.
        @type relative_path: unicode

        @param context: The dictionary used by the exporter to maintain any
            contextual information it many need throgout the export process.
        
            If a context is provided and it contains an 'existing_folders' key,
            it should be a set of strings representing paths that are known to
            be present at the destination. If given, folders in the set will be
            skipped, and those that are created will be added to the set. This
            mechanism can be useful when calling this method repeatedly, to
            avoid unnecessary calls to L{create_folder}.
        @type existing_folders: unicode set
        """
        existing_folders = context.get("existing_folders")

        def ascend(folder):
            if folder and \
            (existing_folders is None or folder not in existing_folders):
                ascend(os.path.dirname(folder))
                created = self.create_folder(folder, context)
                if existing_folders and created:
                    existing_folders.add(folder)

        ascend(relative_path)

    @abstractmethod
    def create_folder(self, relative_path, context):
        """Creates a folder on the destination, if it doesn't exist yet.

        @param relative_path: The path of the folder to create, relative to the
            destination's root.
        @type relative_path: unicode

        @param context: The dictionary used by the exporter to maintain any
            contextual information it many need throgout the export process.
        @type context: dict

        @return: True if the folder didn't exist, and was created, False if it
            already existed.
        @rtype: bool
        """

    def _get_item_contents(self, publishable):
        """Gets the contents and hash for the given item.

        @param publishable: The publishable item to process.
        @type publishable: L{Publishable<woost.models.publishable.Publishable>}

        @return: The item's contents, and their hash. The contents can be
            specified using a file-like object, or a filesystem path.
        @rtype: (file-like or str, str)
        """         
        # Fast path for files
        if isinstance(publishable, File) \
        and publishable.controller \
        and publishable.controller.python_name \
        == "woost.controllers.filecontroller.FileController":
            return publishable.file_path, publishable.file_hash
        else:
            # Override the current context
            cms = controller_context["cms"]
            prev_context = controller_context.copy()
            controller_context.clear()
            controller_context["publishable"] = publishable
            controller_context["cms"] = cms
            controller_context["exporting_static_site"] = True

            # Preserve response and request data
            req = cherrypy.request
            prev_req_headers = dict(req.headers.items())
            req.headers.clear()
            prev_req_query_string = req.query_string
            req.query_string = ""
            prev_req_path_info = req.path_info
            req.path_info = cms.uri(publishable).encode("utf-8")
            prev_req_params = dict(req.params.items())
            
            res = cherrypy.response
            prev_res_headers = dict(res.headers.items())
            res.headers.clear()
            prev_res_status = res.status

            # Use relative URIs on all rendered markup
            if publishable.per_language_publication:
                controller_context["uri_prefix"] = "../"
            else:
                controller_context["uri_prefix"] = "./"

            # Produce the item's content using its controller
            try:
                controller = publishable.resolve_controller()
                
                if isinstance(controller, type):
                    controller = controller()
                
                output = controller()

            # Any kind of redirection or HTTP error must be wrapped and
            # propagated to the user as an exception
            except (cherrypy.HTTPRedirect, cherrypy.HTTPError), ex:
                raise RuntimeError(
                    "Raised error %r while invoking the controller for %s"
                    % (ex, publishable)
                )
            # Restore the preserved context and request/response data
            finally:
                controller_context.clear()
                controller_context.update(prev_context)

                req.headers.update(prev_req_headers)
                req.query_string = prev_req_query_string
                req.path_info = prev_req_path_info
                req.params = prev_req_params

                res.headers.update(prev_res_headers)
                res.status = prev_res_status

            # Wrap the produced content in a buffer, and calculate its hash
            buffer = StringIO()
            hash = md5()
            encoding = publishable.encoding

            if isinstance(output, basestring):
                if encoding and isinstance(output, unicode):
                    output = output.encode(encoding)
                buffer.write(output)
                hash.update(output)
            else:
                for chunk in output:
                    if encoding and isinstance(chunk, unicode):
                        chunk = chunk.encode(encoding)
                    buffer.write(chunk)
                    hash.update(chunk)

            buffer.seek(0)
        
        return buffer, hash.digest()

    @abstractmethod
    def write_file(self, file, path, context):
        """Writes a file to the destination.

        @param file: The file to write. Can be a given as a path to a local
            file, or as a file-like object.
        @type file: str or file-like object

        @param path: The relative path within the exporter's designated
            destination where the file should be written. Must include the
            file's name (and extension, if any).
        @type path: str

        @param context: A dictionary used by the exporter to maintain
            contextual information across its operations (ie. an open
            connection to an FTP server, an instance of a ZipFile class, etc).
        @type context: dict
        """


class StatusTracker(object):
    """An object that allows clients to be kept up to date of the progress of
    an L{export operation<StaticSiteExporter.export>}.
    """
    __metaclass__ = EventHub

    beginning = Event(
        """An event triggered after an exporter has finished its preparations
        and is ready to start the export operation.
        
        @ivar selection: The list of publishable items to be exported. Note
            that some of these items may end up being ignored, if they are not
            published or if they have their X{exportable_as_static_content}
            member set to False.
        @type selection: L{Publishable<woost.models.publishable.Publishable>}
            sequence

        @ivar languages: The list of languages to export the content in.
        @type languages: str sequence

        @ivar context: The L{context<StaticSiteExporter.setup.context>}
            used by the export operation to maintain its state.
        @type context: dict
        """)

    item_processed = Event(
        """An event triggered after an item has been processed.

        This event will be triggered at least once for each item in the
        selection of items to be exported. Items with more than one exported
        translation will invoke the event multiple times (one per language).

        The event will be triggered regardless of the outcome of the exporting
        process, and even if the item is discarded and not exported. Clients
        can differentiate between these cases using the L{status} attribute.

        @ivar publishable: The processed item.
        @type publishable: L{Publishable<woost.models.publishable.Publishable>}

        @ivar status: The status for the processed item. Will be one of the
            following:
                - ignored: The item is not published or marked as not able
                  to be exported, and has been skipped.
                - not-modified: The item hasn't been modified since the last
                  time it was exported, and the operation has been flagged as
                  "L{update only<StaticSiteExporter.export.update_only>}".
                - exported: The item has been correctly exported.
                - failed: The export attempt raised an exception.
        @type status: str

        @ivar language: The language that the item has been processed in.
        @type language: str

        @ivar error: Only relevant if L{status} is 'failed'. A reference
            to the exception raised while trying to export the item.
        @type error: L{Exception}

        @ivar error_handled: Only relevant if L{status} is 'failed'. Allows
            the event response code to capture an export error. If set to True,
            the exporter will continue 
        @type error_handled: bool

        @ivar context: The L{context<StaticSiteExporter.setup.context>}
            used by the export operation to maintain its state.
        @type context: dict
        """)


class FolderStaticSiteExporter(StaticSiteExporter):
    """A class that exports a static snapshot of a site's content to a local
    folder.
    """
    instantiable = True
    
    target_folder = schema.String(
        required = True,
        unique = True
    )

    def __translate__(self, language, **kwargs):
        return (self.draft_source is None and self.target_folder) \
            or StaticSiteExporter.__translate__(self, language, **kwargs)

    def create_folder(self, folder, context):
        full_path = os.path.join(self.target_folder, folder)
        if not os.path.exists(full_path):
            os.mkdir(full_path)

    def write_file(self, file, path, context):

        full_path = os.path.join(self.target_folder, path)

        # Copy local files
        if isinstance(file, str):
            copy(file, full_path)
        
        # Save data from file-like objects
        else:
            target_file = open(full_path, "wb")
            try:
                while True:
                    chunk = file.read(self.chunk_size)
                    if not chunk:
                        break
                    target_file.write(chunk)
            finally:
                target_file.close()


class FTPStaticSiteExporter(StaticSiteExporter):
    """A class that exports a static snapshot of a site's content to an FTP
    server.
    """
    instantiable = True

    members_order = [
        "ftp_host",
        "ftp_user",
        "ftp_password",
        "ftp_path"
    ]

    ftp_host = schema.String(required = True)

    ftp_user = schema.String()

    ftp_password = schema.String(
        edit_control = "cocktail.html.PasswordBox"
    )

    ftp_path = schema.String()

    def __translate__(self, language, **kwargs):

        if self.draft_source is None:
            
            desc = self.ftp_host
            if desc:
                
                user = self.ftp_user
                if user:
                    desc = user + "@" + desc
                
                path = self.ftp_path
                if path:
                    if not path[0] == "/":
                        path = "/" + path
                    desc += path

                return "ftp://" + desc
                
        return StaticSiteExporter.__translate__(self, language, **kwargs)

    def setup(self, context):
        context["ftp"] = ftplib.FTP(
            self.ftp_host,
            self.ftp_user,
            self.ftp_password
        )

    def cleanup(self, context):
        context["ftp"].quit()

    def write_file(self, file, path, context):
        
        ftp = context["ftp"]
        path = self._get_ftp_path(path)

        # Remove existing files
        try:
            ftp.delete(path)
        except ftplib.error_perm:
            pass
        
        # Handle both local files and file-like objects
        if isinstance(file, str):
            file = open(file, "r")
            should_close = True
        else:
            should_close = False
            
        try:
            ftp.storbinary("STOR " + path, file, self.chunk_size)
        finally:
            if should_close:
                file.close()
        
    def create_folder(self, folder, context):
        
        ftp = context["ftp"]
        path = self._get_ftp_path(folder)

        if not self._path_exists(ftp, path):
            ftp.mkd(path)

    def _get_ftp_path(self, *args):

        path = self.ftp_path

        if not path:
            path = "/"
        elif path[-1] != "/":
            path += "/"

        return path + "/".join(arg.strip("/") for arg in args)

    def _path_exists(self, ftp, path):

        path = path.rstrip("/")

        if not path:
            return True        
        
        pos = path.rfind("/")
        
        if pos == -1:
            parent = "."
            name = path
        else:
            parent = path[:pos]
            name = path[pos + 1:]

        return name in ftp.nlst(parent)


class ZipStaticSiteExporter(StaticSiteExporter):
    """A class that exports a static snapshot of a site's content to a ZIP
    file.
    """
    instantiable = True

    def __translate__(self, language, **kwargs):
        return translations(
            "woost.extensions.staticsite.staticsiteexporter."
            "ZipStaticSiteExporter-instance",
            language,
            **kwargs
        )

    def create_folder(self, folder):
        pass

