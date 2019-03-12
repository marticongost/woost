#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from warnings import warn
import os
import hashlib
import fnmatch
from zipfile import ZipFile
from weakref import WeakKeyDictionary
from mimetypes import guess_type
from shutil import copy, copyfileobj
import urllib2
from tempfile import mkdtemp
from shutil import rmtree
from cocktail.events import event_handler
from cocktail.memoryutils import format_bytes
from cocktail import schema
from cocktail.persistence import datastore
from woost import app
from .publishable import Publishable
from .controller import Controller


class File(Publishable):

    instantiable = True
    cacheable_server_side = False
    type_group = "resource"
    backoffice_listing_includes_thumbnail_column = True

    edit_node_class = \
        "woost.controllers.backoffice.fileeditnode.FileEditNode"
    backoffice_card_view = "woost.views.FileCard"
    video_player = "cocktail.html.MediaElementVideo"

    default_mime_type = None
    default_encoding = None

    zip_excluded_patterns = [
        "._*"
    ]

    members_order = [
        "title",
        "file_name",
        "file_size",
        "file_hash"
    ]

    title = schema.String(
        indexed = True,
        normalized_index = True,
        full_text_indexed = True,
        descriptive = True,
        translated = True,
        spellcheck = True,
        member_group = "content"
    )

    file_name = schema.String(
        required = True,
        editable = schema.READ_ONLY,
        member_group = "content"
    )

    file_size = schema.Integer(
        required = True,
        editable = schema.READ_ONLY,
        translate_value = lambda size, language = None, **kwargs:
            "" if size in (None, "") else format_bytes(size),
        min = 0,
        member_group = "content"
    )

    file_hash = schema.String(
        visible = False,
        searchable = False,
        text_search = False,
        member_group = "content"
    )

    def __init__(self, file = None, **kwargs):

        Publishable.__init__(self, **kwargs)

        if file is not None:
            self._v_initializing = True
            self.import_file(
                file,
                guess_mime_type = not self.mime_type,
                compute_hash = not self.file_hash,
                compute_size = not self.file_size,
                assign_file_name = not self.file_name
            )
            self._v_initializing = False

    @property
    def file_extension(self):
        return os.path.splitext(self.file_name)[1]

    @property
    def file_path(self):
        return app.path("upload", str(self.require_id()))

    def import_file(
        self,
        source,
        dest = None,
        guess_mime_type = True,
        compute_hash = True,
        compute_size = True,
        assign_file_name = True,
        encoding = "utf-8",
        download_temp_folder = None,
        user_agent = None,
        redownload = False
    ):
        is_path = isinstance(source, basestring)

        if is_path:

            file_name = os.path.split(source)[1]

            # Download remote files
            if "://" in source:
                if not download_temp_folder:
                    download_temp_folder = mkdtemp()

                temp_path = os.path.join(download_temp_folder, file_name)

                if redownload or not os.path.exists(temp_path):
                    opener = urllib2.build_opener()
                    if user_agent:
                        opener.addheaders = [("User-Agent", user_agent)]
                    response = opener.open(source)

                    with open(temp_path, "w") as temp_file:
                        copyfileobj(response, temp_file)

                source = temp_path

            if encoding and isinstance(file_name, str):
                file_name = file_name.decode(encoding)

            if assign_file_name:
                self.file_name = file_name

            if compute_size:
                self.file_size = os.stat(source).st_size

            if guess_mime_type:
                mime_type = guess_type(file_name, strict = False)
                if mime_type:
                    self.mime_type = mime_type[0]
        else:
            if compute_size:
                source.seek(0, 2)
                self.file_size = source.tell()
                source.seek(0)

        if compute_hash:
            self.file_hash = file_hash(source)
            if not is_path:
                source.seek(0)

        if dest is None:
            upload_path = self.file_path
        else:
            upload_path = os.path.join(dest, str(self.require_id()))

        if is_path:
            copy(source, upload_path)
        else:
            with open(upload_path, "wb") as upload:
                copyfileobj(source, upload)

    @classmethod
    def import_zip_contents(cls, zip_file, **new_file_options):
        """Create instances of this class to represent each of the files
        contained within the given ZIP file.

        Note that calling the method on a subclass of `File` will create
        objects of that class.

        :param zip_file: The ZIP file to import. Can be given as a filesystem
            path pointing to a ZIP file, an open file-like object or an
            instance of `zipfile.ZipFile`.
        :type zip_file: str, file like or `zipfile.ZipFile`

        :param new_file_options: Keyword arguments to be forwarded to the
            `File.import_file` method.

        :return: A list containing all the `File` objects created by the
            method.
        :rtype: [File]
        """
        files = []

        if not isinstance(zip_file, ZipFile):
            zip_file = ZipFile(zip_file, "r")

        temp_dir = mkdtemp()
        try:
            zip_file.extractall(temp_dir)
            for root, dirs, file_names in os.walk(temp_dir):
                for file_name in file_names:
                    # Import a file only if it matches none of the defined excluded patterns
                    if not all([
                        fnmatch.fnmatch(file_name, pattern)
                        for pattern in cls.zip_excluded_patterns
                    ]):
                        new_file = cls.new()
                        path = os.path.join(root, file_name)
                        new_file.import_file(path, **new_file_options)
                        files.append(new_file)
        finally:
            rmtree(temp_dir)

        return files

    @classmethod
    def from_path(
        cls,
        path,
        dest = None,
        languages = None,
        hash = None,
        encoding = "utf-8",
        download_temp_folder = None,
        redownload = False
    ):
        """Imports a file into the site.

        @param path: The path to the file that should be imported.
        @type path: str

        @param dest: The base path where the file should be copied (should match
            the upload folder for the application).
        @type dest: str

        @param languages: The set of languages that the created file will be
            translated into.
        @type languages: str set

        @return: The created file.
        @rtype: L{File}
        """
        warn(
            "File.from_path() is deprecated, use File.import_file() or the "
            "'file' argument of the File constructor",
            DeprecationWarning,
            stacklevel = 2
        )

        file = cls()
        file.import_file(
            path,
            dest = dest,
            compute_hash = not hash,
            encoding = encoding,
            download_temp_folder = download_temp_folder,
            redownload = redownload
        )

        if hash:
            file.file_hash = hash

        # The default behavior is to translate created files into all the languages
        # defined by the site
        if languages is None:
            from woost.models import Configuration
            languages = Configuration.instance.languages

        file_name = os.path.split(path)[1]
        title, ext = os.path.splitext(file_name)

        title = title.replace("_", " ").replace("-", " ")
        title = title[0].upper() + title[1:]

        for language in languages:
            file.set("title", title, language)

        return file

    def create_copy(self, *args, **kwargs):

        clone = Publishable.create_copy(self, *args, **kwargs)

        # Copy the phisical file once the transaction is complete
        if self.id:
            key = "woost.models.File.duplicates"
            dup_files = datastore.get_transaction_value(key)

            if dup_files is None:
                dup_files = WeakKeyDictionary()
                datastore.set_transaction_value(key, dup_files)
                datastore.unique_after_commit_hook(
                    "woost.models.File.duplicate",
                    _duplicate_files_after_commit,
                    dup_files
                )

            dup_files[clone] = self

        return clone


def _duplicate_files_after_commit(success, dup_files):
    if success:
        for clone, source in dup_files.iteritems():
            if clone.is_inserted:
                copy(source.file_path, clone.file_path)

def file_hash(source, algorithm = "md5", chunk_size = 1024):
    """Obtains a hash for the contents of the given file.

    @param source: The file to obtain the hash for. Can be given as a file
        system path, or as a reference to a file like object.
    @type source: str or file like object

    @param algorithm: The hashing algorithm to use. Takes the same values as
        L{hashlib.new}.
    @type algorithm: str

    @param chunk_size: The size of the file chunks to read from the source, in
        bytes.
    @type chunk_size: int

    @return: The resulting file hash, in binary form.
    @rtype: str
    """
    hash = hashlib.new(algorithm)

    if isinstance(source, basestring):
        should_close = True
        source = open(source, "r")
    else:
        should_close = False

    try:
        while True:
            chunk = source.read(chunk_size)
            if not chunk:
                break
            hash.update(chunk)
    finally:
        if should_close:
            source.close()

    return hash.hexdigest()

