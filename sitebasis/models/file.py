#-*- coding: utf-8 -*-
u"""

@var extensions: A dictionary mapping extensions to MIME types.
@var extensions: dict(str, str)

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
import hashlib
import os
from shutil import copy
from cocktail.modeling import getter
from cocktail.events import event_handler
from cocktail import schema
from cocktail.controllers import context
from sitebasis.models.resource import Resource
from sitebasis.models.language import Language

extension_mime_types = {
    "ai": "application/postscript",
    "aif": "audio/x-aiff",
    "aifc": "audio/x-aiff",
    "aiff": "audio/x-aiff",
    "asc": "text/plain",
    "au": "audio/basic",
    "avi": "video/x-msvideo",
    "bcpio": "application/x-bcpio",
    "bin": "application/octet-stream",
    "bmp": "image/bmp",
    "bz": "application/x-bzip",
    "c": "text/plain",
    "cab": "vnd.ms-cab-compressed",
    "cc": "text/plain",
    "ccad": "application/clariscad",
    "cdf": "application/x-netcdf",
    "class": "application/octet-stream",
    "cpio": "application/x-cpio",
    "cpt": "application/mac-compactpro",
    "csh": "application/x-csh",
    "css": "text/css",
    "dcr": "application/x-director",
    "dir": "application/x-director",
    "dms": "application/octet-stream",
    "doc": "application/msword",
    "drw": "application/drafting",
    "dvi": "application/x-dvi",
    "dwg": "application/acad",
    "dxf": "application/dxf",
    "dxr": "application/x-director",
    "eps": "application/postscript",
    "etx": "text/x-setext",
    "exe": "application/octet-stream",
    "ez": "application/andrew-inset",
    "f": "text/plain",
    "f90": "text/plain",
    "fli": "video/x-fli",
    "gif": "image/gif",
    "gtar": "application/x-gtar",
    "gz": "application/x-gzip",
    "h": "text/plain",
    "hdf": "application/x-hdf",
    "hh": "text/plain",
    "hqx": "application/mac-binhex40",
    "htm": "text/html",
    "html": "text/html",
    "ice": "x-conference/x-cooltalk",
    "ief": "image/ief",
    "iges": "model/iges",
    "igs": "model/iges",
    "ips": "application/x-ipscript",
    "ipx": "application/x-ipix",
    "jpe": "image/jpeg",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "js": "application/x-javascript",
    "kar": "audio/midi",
    "latex": "application/x-latex",
    "lha": "application/octet-stream",
    "lsp": "application/x-lisp",
    "lzh": "application/octet-stream",
    "m": "text/plain",
    "man": "application/x-troff-man",
    "mdb": "application/msaccess",
    "me": "application/x-troff-me",
    "mesh": "model/mesh",
    "mid": "audio/midi",
    "midi": "audio/midi",
    "mif": "application/vnd.mif",
    "mime": "www/mime",
    "mov": "video/quicktime",
    "movie": "video/x-sgi-movie",
    "mp2": "audio/mpeg",
    "mp3": "audio/mpeg",
    "mpe": "video/mpeg",
    "mpeg": "video/mpeg",
    "mpg": "video/mpeg",
    "mpga": "audio/mpeg",
    "ms": "application/x-troff-ms",
    "msh": "model/mesh",
    "nc": "application/x-netcdf",
    "oda": "application/oda",
    "odp": "application/vnd.oasis.opendocument.presentation",
    "ods": "application/vnd.oasis.opendocument.spreadsheet",
    "odt": "application/vnd.oasis.opendocument.text",
    "pbm": "image/x-portable-bitmap",
    "pdb": "chemical/x-pdb",
    "pdf": "application/pdf",
    "pgm": "image/x-portable-graymap",
    "pgn": "application/x-chess-pgn",
    "png": "image/png",
    "pnm": "image/x-portable-anymap",
    "pot": "application/mspowerpoint",
    "ppm": "image/x-portable-pixmap",
    "pps": "application/mspowerpoint",
    "ppt": "application/mspowerpoint",
    "ppz": "application/mspowerpoint",
    "pre": "application/x-freelance",
    "prt": "application/pro_eng",
    "ps": "application/postscript",
    "py": "text/plain",
    "pyc": "application/octet-stream",
    "qt": "video/quicktime",
    "ra": "audio/x-realaudio",
    "ram": "audio/x-pn-realaudio",
    "rar": "application/x-rar-compressed",
    "ras": "image/cmu-raster",
    "rgb": "image/x-rgb",
    "rm": "audio/x-pn-realaudio",
    "roff": "application/x-troff",
    "rpm": "audio/x-pn-realaudio-plugin",
    "rtf": "text/rtf",
    "rtx": "text/richtext",
    "scm": "application/x-lotusscreencam",
    "set": "application/set",
    "sgm": "text/sgml",
    "sgml": "text/sgml",
    "sh": "application/x-sh",
    "shar": "application/x-shar",
    "silo": "model/mesh",
    "sit": "application/x-stuffit",
    "skd": "application/x-koan",
    "skm": "application/x-koan",
    "skp": "application/x-koan",
    "skt": "application/x-koan",
    "smi": "application/smil",
    "smil": "application/smil",
    "snd": "audio/basic",
    "sol": "application/solids",
    "spl": "application/x-futuresplash",
    "src": "application/x-wais-source",
    "step": "application/STEP",
    "stl": "application/SLA",
    "stp": "application/STEP",
    "sv4cpio": "application/x-sv4cpio",
    "sv4crc": "application/x-sv4crc",
    "swf": "application/x-shockwave-flash",
    "t": "application/x-troff",
    "tar": "application/x-tar",
    "tcl": "application/x-tcl",
    "tex": "application/x-tex",
    "texi": "application/x-texinfo",
    "texinfo": "application/x-texinfo",
    "tif": "image/tiff",
    "tiff": "image/tiff",
    "tr": "application/x-troff",
    "tsi": "audio/TSP-audio",
    "tsp": "application/dsptype",
    "tsv": "text/tab-separated-values",
    "txt": "text/plain",
    "unv": "application/i-deas",
    "ustar": "application/x-ustar",
    "vcd": "application/x-cdlink",
    "vda": "application/vda",
    "viv": "video/vnd.vivo",
    "vivo": "video/vnd.vivo",
    "vrml": "model/vrml",
    "wav": "audio/x-wav",
    "wrl": "model/vrml",
    "xbm": "image/x-xbitmap",
    "xhtml": "application/xhtml",
    "xlc": "application/vnd.ms-excel",
    "xll": "application/vnd.ms-excel",
    "xlm": "application/vnd.ms-excel",
    "xls": "application/vnd.ms-excel",
    "xlw": "application/vnd.ms-excel",
    "xml": "text/xml",
    "xpm": "image/x-xpixmap",
    "xwd": "image/x-xwindowdump",
    "xyz": "chemical/x-pdb",
    "zip": "application/zip"
}

mime_type_categories = {}

for category, mime_types in (
    ("text/plain", ("text",)),
    ("html_resource", (
        "text/css",
        "text/javascript",
        "text/ecmascript",
        "application/javascript",
        "application/ecmascript"
    )),
    ("document", (
        "application/vnd.oasis.opendocument.text",
        "application/vnd.oasis.opendocument.spreadsheet",
        "application/vnd.oasis.opendocument.presentation",
        "application/msword",
        "application/msexcel",
        "application/msaccess",
        "application/mspowerpoint",
        "application/mswrite",
        "application/vnd.ms-excel",
        "application/vnd.ms-access",
        "application/vnd.ms-powerpoint",
        "application/vnd.ms-project",
        "application/vnd.ms-works",
        "application/vnd.ms-xpsdocument",
        "application/rtf",
        "application/pdf",
        "application/postscript",
        "application/x-latex",
        "application/vnd.oasis.opendocument.database"
    )),
    ("package", (
        "application/zip",
        "application/x-rar-compressed",
        "application/x-tar",
        "application/x-gtar",
        "application/x-gzip",
        "application/x-bzip",
        "application/x-stuffit",
        "vnd.ms-cab-compressed"
    ))
):
    for mime_type in mime_types:
        mime_type_categories[mime_type] = category


class File(Resource):
 
    instantiable = True

    edit_view = "sitebasis.views.FileFieldsView"
    edit_node_class = \
        "sitebasis.controllers.backoffice.fileeditnode.FileEditNode"

    members_order = [
        "file_name",
        "mime_type"
    ]

    file_name = schema.String(
        required = True,
        editable = False
    )

    mime_type = schema.String(
        required = True,
        editable = False,
        text_search = False
    )

    file_size = schema.Integer(
        required = True,
        editable = False,
        min = 0
    )

    file_hash = schema.String(
        visible = False,
        searchable = False
    )

    @getter
    def uri(self):
        return context["cms"].application_uri("files", self.id)

    @getter
    def file_path(self):
        return context["cms"].get_file_upload_path(self.id)

    @event_handler
    def handle_changed(cls, event):
        # Update the 'file_category' member when 'mime_type' is set

        file = event.source

        if event.member.name == "mime_type":
            file.resource_type = get_category_from_mime_type(file.mime_type)

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
        file.mime_type = get_extension_mime_type(ext[1:])
        file.file_size = os.stat(path).st_size
        file.file_hash = file_hash(path)
        file.file_name = file_name
        
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

def get_category_from_mime_type(mime_type):
    """Obtains the file category that best matches the indicated MIME type.
    
    @param mime_type: The MIME type to get the category for.
    @type mime_type: str

    @return: A string identifier with the category matching the indicated
        MIME type (one of 'document', 'image', 'audio', 'video', 'package',
        'html_resource' or 'other').
    @rtype: str
    """
    pos = mime_type.find("/")

    if pos != -1:
        prefix = mime_type[:pos]

        if prefix in ("image", "audio", "video"):
            return prefix
    
    return mime_type_categories.get(mime_type, "other")

def get_extension_mime_type(extension):
    """Obtains the MIME type that matches the given extension.

    @param extension: The extension to get the MIME type for.
    @type extension: str

    @return: The MIME type for the indicated extension.
    @rtype: str

    @raise ValueError: Raised if there's no known match for the given
        extension.
    """
    try:
        return extension_mime_types[extension]
    except KeyError:
        raise ValueError("No known MIME type match for extension " + extension)

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
    """Return a string representing the greek/metric suffix of a file size."""
    for factor, suffix in _size_suffixes:
        if size > factor:
            break
    return str(int(size/factor)) + suffix

