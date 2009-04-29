#-*- coding: utf-8 -*-
"""
Definition of standard document resolvers.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2009
"""
import re
from cocktail.modeling import abstractmethod
from sitebasis.models import Site, Document


class DocumentResolver(object):
    """Base class for all document resolvers.
    
    Document resolvers are used by the L{CMS<sitebasis.controllers.application.CMS>}
    class to map documents to application paths, and viceversa.
    """
    
    @abstractmethod
    def get_document(self,
        path,
        consume_path = False,
        canonical_redirection = False):
        """Obtains the document that matches the indicated path.
    
        @param path: The path to evaluate; A list-like object describing a
            relative application path.
        @type path: str list

        @param consume_path: If set to True, implementations should remove from
            the list any path component that they use when determining the
            matched object. If set to False, the list shouldn't be modified.
        @type consume_path: bool
        
        @param canonical_redirection: If set to True, implementations should
            trigger a redirection to a document's canonical location when the
            given path matches a document using one of its non canonical
            paths.
            
            What constitutes a canonical path is for implementations to decide.
            The concept of a canonical path may be not applicable to some
            resolvers; in that case, implementations should ignore this flag.
        @type canonical_redirection: True

        @return: The matching document, or None if there's no document matching
            the indicated path.
        @rtype: L{Document<sitebasis.models.document.Document>}
        """

    @abstractmethod
    def get_path(self, document):
        """Obtains the canonical path for the indicated document, relative to
        the application's root.
        
        @param document: The document to get the path for.
        @type document: L{Document<sitebasis.models.document.Document>}

        @param language: The language that the produced URI will be translated
            into. If omitted, the active language will be used instead. This
            parameter only makes sense on certain implementations, and should
            be ignored by implementations that can't make use of it.
        @type language: str

        @return: The relative path for the document.
        @rtype: str
        """


class HierarchicalPathResolver(DocumentResolver):
    """A resolver that publishes documents following a name hierarchy.

    The name hierarchy is defined by the
    L{path<sitebasis.models.Document.path>},
    L{full_path<sitebasis.models.Document.full_path>} and
    L{parent<sitebasis.models.Document.parent>} members of the
    L{Document<sitebasis.models.Document>} class."""

    def get_document(self,
        path,
        consume_path = False,
        canonical_redirection = False):

        docpath = list(path)
        
        while docpath:
            document = Document.get_instance(full_path = "/".join(docpath))
            if document:
                break
            else:
                docpath.pop()
        else:
            document = Site.main.home
        
        if consume_path:
            for component in docpath:
                path.pop(0)

        return document

    def get_path(self, document, language = None):
        return document.full_path or ""


class IdResolver(DocumentResolver):
    """A document resolver based on document ids."""

    def get_document(self,
        path,
        consume_path = False,
        canonical_redirection = False):

        if path:
            id = path.pop(0) if consume_path else path[0]

            try:
                id = int(id)
            except:
                return None

            if canonical_redirection and id == Site.main.home.id:
                raise CanonicalURIRedirection("")

            return Document.get_instance(id)
        else:
            return Site.main.home

    def get_path(self, document, language = None):
        return str(document.id)


class DescriptiveIdResolver(DocumentResolver):
    """A document resolver that combines a unique identifier and a descriptive
    text fragment.

    @ivar word_separator: The character used for separating words on a
        document's title to conform the descriptive fragment of its URI.
    @type word_separator: str

    @ivar id_regexp: The regular expression used to extract the unique
        identifier from a document's URI. The expression must define an 'id'
        named group. 
    @type id_regexp: regular expression
    
    @param format: A python formatting string, used for composing a document's
        URI from its unique identifier and flattened title.
    @type format: str
    """
    id_separator = "_"
    word_separator = "-"
    id_regexp = re.compile(r"([^_]+_)?(?P<id>\d+)$")
    format = "%(title)s_%(id)d"
    _title_regexp = re.compile(r"\W+", re.UNICODE)

    def get_document(self,
        path,
        consume_path = False,
        canonical_redirection = False):

        if path:

            ref = path.pop(0) if consume_path else path[0]
            
            if not isinstance(ref, unicode):
                ref = ref.decode("utf-8")

            # Discard descriptive text
            match = self.id_regexp.match(ref)

            if match is None:
                return None
            else:
                id = match.group("id")

            try:
                id = int(id)
            except:
                return None

            document = Document.get_instance(id)
            
            if canonical_redirection \
            and document is not None:                
                canonical_ref = self.get_path(document)
                if ref != canonical_ref:
                    raise CanonicalURIRedirection(canonical_ref)
            
            return document
        else:
            return Site.main.home

    def get_path(self, document, language = None):
        
        if document is Site.main.home:
            return ""
        else:
            title = document.get("title", language)

            if title:
                title = self._title_regexp.sub(
                    self.word_separator,
                    title
                )
                title = title.lower()            
                ref = self.format % {
                    "title": title,
                    "id": document.id
                }
            else:
                ref = str(document.id)

            return ref


class CanonicalURIRedirection(Exception):
    """Represents a redirection to the canonical form of the current URI.
    
    @ivar path: A relative path, representing the canonical URI for the current
        request.
    @type path: str
    """

    def __init__(self, path):
        self.path = path

