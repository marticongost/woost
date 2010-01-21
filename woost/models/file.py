#-*- coding: utf-8 -*-
u"""

@var extensions: A dictionary mapping extensions to MIME types.
@var extensions: dict(str, str)

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import os
import hashlib
from mimetypes import guess_type
from shutil import copy
from cocktail.modeling import getter
from cocktail.events import event_handler
from cocktail import schema
from cocktail.controllers import context
from woost.models.publishable import Publishable
from woost.models.controller import Controller
from woost.models.language import Language


class File(Publishable):
 
    edit_view = "woost.views.FileFieldsView"
    edit_node_class = \
        "woost.controllers.backoffice.fileeditnode.FileEditNode"

    default_controller = schema.DynamicDefault(
        lambda: Controller.get_instance(qname = "woost.file_controller")
    )

    members_order = [
        "file_name",
        "file_size",
        "file_hash"
    ]

    file_name = schema.String(
        required = True,
        editable = False
    )

    file_size = schema.Integer(
        required = True,
        editable = False,
        translate_value = lambda size:
            "" if size in (None, "") else get_human_readable_file_size(size),
        min = 0
    )

    file_hash = schema.String(
        visible = False,
        searchable = False
    )

    @getter
    def file_path(self):
        return context["cms"].get_file_upload_path(self.id)

    @classmethod
    def from_path(cls,
        path,
        dest,
        languages = None):
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
        
        # The default behavior is to translate created files into all the languages
        # defined by the site
        if languages is None:
            languages = Language.codes

        file_name = os.path.split(path)[1]
        title, ext = os.path.splitext(file_name)
        title = title.replace("_", " ").replace("-", " ")
        title = title[0].upper() + title[1:]

        file = cls()
        
        file.file_size = os.stat(path).st_size
        file.file_hash = file_hash(path)
        file.file_name = file_name

        # Infer the file's MIME type
        mime_type = guess_type(file_name)
        if mime_type:
            file.mime_type = mime_type[0]
        
        for language in languages:
            file.set("title", title, language)

        upload_path = os.path.join(dest, str(file.id))           
        copy(path, upload_path)

        return file


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

    return hash.digest()

# Adapted from a script by Martin Pool, original found at
# http://mail.python.org/pipermail/python-list/1999-December/018519.html
_size_suffixes = [
    (1<<50L, 'Pb'),
    (1<<40L, 'Tb'), 
    (1<<30L, 'Gb'), 
    (1<<20L, 'Mb'), 
    (1<<10L, 'kb'),
    (1, 'bytes')
]

def get_human_readable_file_size(size):
    """Return a string representing the greek/metric suffix of a file size.
    
    @param size: The size to represent, in bytes.
    @type size: int

    @return: The metric representation of the given size.
    @rtype: str
    """
    for factor, suffix in _size_suffixes:
        if size > factor:
            break
    return str(int(size/factor)) + suffix


