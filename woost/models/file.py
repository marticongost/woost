#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from warnings import warn
import os
import hashlib
from weakref import WeakKeyDictionary
from mimetypes import guess_type
from shutil import copy, copyfileobj
import urllib.request, urllib.error, urllib.parse
from tempfile import mkdtemp
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
    admin_show_descriptions = False
    admin_show_thumbnails = True
    ui_display = "woost.admin.ui.ItemCard"
    _v_upload_id = None

    edit_node_class = \
        "woost.controllers.backoffice.fileeditnode.FileEditNode"
    backoffice_card_view = "woost.views.FileCard"
    video_player = "cocktail.html.MediaElementVideo"

    default_mime_type = None
    default_encoding = None

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
        editable = schema.NOT_EDITABLE,
        member_group = "content"
    )

    file_size = schema.Integer(
        required = True,
        editable = schema.NOT_EDITABLE,
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
    def image_id(self):
        if self._v_upload_id:
            return "upload-" + self._v_upload_id
        else:
            return str(self.id) if self.id else None

    @property
    def file_extension(self):
        return self.file_name and os.path.splitext(self.file_name)[1] or None

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
        is_path = isinstance(source, str)

        if is_path:

            file_name = os.path.split(source)[1]

            # Download remote files
            if "://" in source:
                if not download_temp_folder:
                    download_temp_folder = mkdtemp()

                temp_path = os.path.join(download_temp_folder, file_name)

                if redownload or not os.path.exists(temp_path):
                    opener = urllib.request.build_opener()
                    if user_agent:
                        opener.addheaders = [("User-Agent", user_agent)]
                    response = opener.open(source)

                    with open(temp_path, "w") as temp_file:
                        copyfileobj(response, temp_file)

                source = temp_path

            if encoding and isinstance(file_name, bytes):
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

    @event_handler
    def handle_deleted(cls, e):
        TRANSACTION_KEY = "woost.models.File.deleted_instances"
        deleted_files = datastore.get_transaction_value(TRANSACTION_KEY)
        if deleted_files is None:
            deleted_files = {e.source}
            datastore.set_transaction_value(TRANSACTION_KEY, deleted_files)
            datastore.unique_after_commit_hook(
                "woost.models.File.delete_files",
                _delete_files_after_commit,
                deleted_files
            )
        else:
            deleted_files.add(e.source)


def _delete_files_after_commit(success, deleted_instances):
    if success:
        for file in deleted_instances:
            try:
                os.remove(file.file_path)
            except OSError:
                warn("Couldn't delete file %s" % file.file_path)

def _duplicate_files_after_commit(success, dup_files):
    if success:
        for clone, source in dup_files.items():
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

    if isinstance(source, str):
        should_close = True
        source = open(source, "rb")
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

