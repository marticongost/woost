#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			January 2010
"""
from __future__ import with_statement
import os
from time import mktime
from shutil import copy
from hashlib import md5
from cStringIO import StringIO
import cherrypy
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

    def export(self, selection = None, languages = None, update_only = False):
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

        @return: The collection of items that were actually exported.
        @rtype: L{Publishable<woost.models.publishable.Publishable>} list
        """
        controller_context["exporting_static_site"] = True

        try:
            context = {"existing_folders": set()}
            self.setup(context)

            if selection is None:
                selection = Publishable.select()

            exported_items = []
            
            if languages is not None \
            and not isinstance(languages, (set, frozenset, SetWrapper)):
                languages = set(languages)

            for item in selection:
                if item.exportable_as_static_content and item.is_published():
                    
                    # Export multiple translations
                    if item.per_language_publication:
                        exported = False
                        
                        if languages:
                            item_languages = \
                                languages.intersection(item.translations)
                        else:
                            item_languages = item.translations

                        for language in item_languages:
                            exported = exported \
                                    or self.export_item(
                                        item,
                                        context,
                                        language = language,
                                        update_only = update_only
                                    )
                    
                    # Items that don't change their publication based on the
                    # language
                    else:
                        exported = self.export_item(
                            item,
                            context,
                            update_only = update_only
                        )

                    if exported:
                        exported_items.append(item)

            return exported_items
        
        finally:
            del controller_context["exporting_static_site"]

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

            self.create_path(folder, context["existing_folders"])
            self.write_file(file, relative_path, context)
            self.__last_export_hashes[publishable.id] = hash
            return True

        if language:
            with language_context(language):
                with content_language_context(language):
                    return export()
        else:
            return export()
    
    def create_path(self, relative_path, existing_folders = None):
        """Recursively creates all folders in the given path.

        The method will invoke L{create_folder} for each folder in the provided
        path.

        @param relative_path: The path to create, relative to the destination's
            root.
        @type relative_path: unicode

        @param existing_folders: A set of folders that are known to be present
            at the destination. If given, folders in the set will be skipped,
            and those that are created will be added to the set. This parameter
            can be useful when calling this method repeatedly, to avoid
            unnecessary calls to L{create_folder}.
        @type existing_folders: unicode set
        """
        def ascend(folder):
            if folder and \
            (existing_folders is None or folder not in existing_folders):
                ascend(os.path.dirname(folder))
                created = self.create_folder(folder)
                if existing_folders and created:
                    existing_folders.add(folder)

        ascend(relative_path)

    @abstractmethod
    def create_folder(self, relative_path):
        """Creates a folder on the destination, if it doesn't exist yet.

        @param relative_path: The path of the folder to create, relative to the
            destination's root.
        @type relative_path: unicode

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
        headers = cherrypy.response.headers
        prev_headers = dict(headers.items())
        
        try:
                    
            # Fast path for files
            if isinstance(publishable, File) \
            and publishable.controller \
            and publishable.controller.python_name \
            == "woost.controllers.filecontroller.FileController":
                return publishable.file_path, publishable.file_hash
            else:
                # Override the current context
                prev_context = controller_context.copy()
                controller_context.clear()
                controller_context["publishable"] = publishable
                controller_context["cms"] = prev_context["cms"]
                controller_context["exporting_static_site"] = True
                
                try:
                    # Produce the item's content using its controller
                    controller = publishable.resolve_controller()
                    
                    if isinstance(controller, type):
                        controller = controller()
                    
                    output = controller()
                finally:
                    controller_context.clear()
                    controller_context.update(prev_context)

                # Wrap the produced content in a buffer, and calculate its hash
                buffer = StringIO()
                hash = md5()

                if isinstance(output, basestring):
                    buffer.write(output)
                    hash.update(output)
                else:
                    for chunk in output:
                        buffer.write(chunk)
                        hash.update(chunk)

                buffer.seek(0)
            
            return buffer, hash.digest()

        except (cherrypy.HTTPRedirect, cherrypy.HTTPError), ex:
            raise RuntimeError(
                "Raised error %r while invoking the controller for %s"
                % (ex, publishable)
            )

        finally:
            headers.clear()
            headers.update(prev_headers)

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

    def create_folder(self, folder):
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

