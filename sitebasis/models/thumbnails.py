#-*- coding: utf-8 -*-
"""
Provides classes that generate thumbnail images for CMS items.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2009
"""
import os
import Image
from cocktail.modeling import abstractmethod
from sitebasis.models import File


class ThumbnailLoader(object):
    """A class that produces thumbnail images for content items.
    
    @var cache_path: A directory used to store copies of generated
        thumbnails, to speed up further thumbnail requests for the same item.
        Clearing this attribute disables thumbnail caching.
    @type cache_path: str

    @param relevant_cache_parameters: A set listing which thumbnail parameters
        to take into account when deciding the file name for cached copies of
        generated thumbnails.
    @type relevant_cache_parameters: str set

    @var default_width: The default width for generated thumbnails.
    @type default_width: int

    @var default_height: The default height for generated thumbnails.
    @type default_height: int

    @var default_format: The default image format for generated thumbnails.
    @type default_format: str

    @var thumbnailers: The list of L{thumbnailers<Thumbnailer>} used by the
        loader to generate the thumbnails. Each thumbnailer can generate
        thumbnails for different content types and sets of parameters.
        Thumbnailers are tried in the order specified by the list.
    @type thumbnailers: L{Thumbnailer} list
    """
    cache_path = None
    relevant_cache_parameters = frozenset()
    default_width = None
    default_height = None
    default_format = "jpeg"
    thumbnailers = []

    def __init__(self):
        self.thumbnailers = []

    def get_thumbnailer(self, item, **params):
        """Gets the L{thumbnailer<Thumbnailer>} that best matches the given
        request.

        @param item: The item to create the thumbnail for.
        @type item: L{Item<sitebasis.models.Item>}

        @param params: A set of formatting options that should be observed by
            the thumbnailer.

        @return: The thumbnailer that is most indicated for the given request,
            or None if there's no registered thumbnailer that can handle the
            request.
        @rtype: L{Thumbnailer}
        """
        for thumbnailer in self.thumbnailers:
            if thumbnailer.can_handle(item, **params):
                return thumbnailer
        else:
            return None

    def _sanitize_request(self, item, width, height):
        
        if item is None:
            raise ThumbnailParameterError(
                "Must specify an item to generate a thumbnail for."
            )

        if width is None and height is None:
            width = self.default_width
            height = self.default_height
    
        if width is None and height is None:
            raise ThumbnailParameterError("Must specify width, height or both")

        if width is not None and (not isinstance(width, int) or width <= 0):
            raise ThumbnailParameterError(
                "Thumbnail width must be a positive integer (got %s instead)."
                % width
            )
    
        if height is not None and (not isinstance(height, int) or height <= 0):
            raise ThumbnailParameterError(
                "Thumbnail height must be a positive integer (got %s instead)."
                % height
            )

        return item, width, height

    def get_cached_thumbnail_path(self,
        item,
        width = None,
        height = None,
        **params):
        """Gets the path to the file where thumbnails for the given request
        will be stored.
        
        @param item: The item represented by the thumbnail.
        @type item: L{Item<sitebasis.models.Item>}

        @param width: The width (in pixels) of the generated thumbnail.
        @type width: int

        @param height: The height (in pixels) of the generated thumbnail.
        @type height: int

        @param params: A set of formatting options that should be observed by
            the thumbnailer.
        
        @return: The path for the requested thumbnail.
        @rtype: str
        """
        item, width, height = self._sanitize_request(item, width, height)

        # Base name
        file_name = "%s-%sx%s" % (item.id, width or "auto", height or "auto")

        # Parameters
        param_list = "-".join(
            "%s:%s" % (key, value)
            for key, value in params.iteritems()
            if key in self.relevant_cache_parameters
        )    
        if param_list:
            file_name += param_list

        # File format
        file_format = params.get("format", self.default_format)
        if file_format:
            file_name += "." + file_format

        return os.path.join(self.cache_path, file_name)

    def get_thumbnail(self, item, width = None, height = None, **params):
        """Gets a thumbnail image for the given item.

        @param item: The item to create the thumbnail for.
        @type item: L{Item<sitebasis.models.Item>}

        @param width: The width (in pixels) of the generated thumbnail.
        @type width: int

        @param height: The height (in pixels) of the generated thumbnail.
        @type height: int

        @param params: A set of formatting options that should be observed by
            the thumbnailer.

        @return: The generated thumbnail.
        @rtype: L{Image<Image.Image>}
        """
        item, width, height = self._sanitize_request(item, width, height)
        
        thumbnailer = self.get_thumbnailer(item, **params)

        if thumbnailer is None:
            return None
    
        image = None

        # Load from cache
        if self.cache_path:
            cached_thumbnail_path = self.get_cached_thumbnail_path(
                item,
                width,
                height,
                **params
            )

            # Make sure cached thumbnails are current
            if os.path.exists(cached_thumbnail_path):
                thumbnail_date = os.stat(cached_thumbnail_path).st_mtime
                if not thumbnailer.thumbnail_changed(item, thumbnail_date):
                    image = Image.open(cached_thumbnail_path)

        # No usable cached copy available, or cache disabled:
        # generate a new thumbnail
        if image is None:
            image = thumbnailer.create_thumbnail(
                item,
                width,
                height,
                **params
            )

            # If caching is enabled, store the generated thumbnail for further
            # requests
            if self.cache_path:
                self.save_thumbnail(image, cached_thumbnail_path, **params)

        return image

    def save_thumbnail(self, image, dest, **params):
        """Writes the given thumbnail image to a file.
        
        @param image: The thumbnail to store.
        @type image: L{Image<Image.Image>}

        @param dest: The file-like object or file path to write the thumbnail
            to.
        @type dest: str or file object
        
        @param params: A set of formatting options that should be observed by
            the thumbnailer.
        """
        format = params.pop("format", self.default_format)
        
        if format is None:
            raise ValueError("Image format not specified")

        format = format.upper()

        # PIL requires an explicit conversion before saving fixed palette
        # images to RGB formats
        if format == "JPEG" and image.mode != "RGB":
            image = image.convert("RGB")
        
        image.save(dest, format, **params)


class ThumbnailParameterError(ValueError):
    """An exception raised when trying to generate a thumbnail using an invalid
    parameter.
    """


class Thumbnailer(object):
    """Thumbnailers generate thumbnail images for certain kinds of items."""

    @abstractmethod
    def can_handle(self, item, **params):
        """Indicates if the thumbnailer can generate the requested thumbnail.

        @param item: The item to create the thumbnail for.
        @type item: L{Item<sitebasis.models.Item>}
        
        @param params: A set of formatting options that should be observed by
            the thumbnailer. Thumbnailers are free to decide they are not
            capable of generating a thumbnail if a particular option is set to
            an unsupported value.

        @return: True if the thumbnailer can generate the requested thumbnail,
            False otherwise.
        @rtype: bool
        """
    
    def thumbnail_changed(self, item, date):
        """Indicates if an item has been changed in a manner that would alter
        its thumbnail from the indicated date.
        
        This method is used by L{thumbnail loaders<ThumbnailLoader>} to
        decide which cached thumbnails should be ditched and created anew.

        @param item: The item to test.
        @type item: L{Item<sitebasis.models.Item>}

        @param date: The point in time from which changes to the item should be
            examined.
        @type: datetime

        @return: True if the item has had changes that would alter its
            thumbnail, False otherwise.
        @rtype: bool
        """
        return item.last_update_time <= date

    @abstractmethod
    def create_thumbnail(self, item, width, height, **params):
        """Creates a thumbnail image for the given item.

        @param item: The item to create the thumbnail for.
        @type item: L{Item<sitebasis.models.Item>}

        @param width: The width (in pixels) of the generated thumbnail.
        @type width: int

        @param height: The height (in pixels) of the generated thumbnail.
        @type height: int

        @param params: A set of formatting options that should be observed by
            the thumbnailer.

        @return: The generated thumbnail.
        @rtype: L{Image<Image.Image>}
        """


class ImageThumbnailer(Thumbnailer):
    """Generates thumbnails for image files."""

    resize_filter = Image.ANTIALIAS

    # TODO: Extend it to all resources, including URI instances
    # (Rename it to ResourceThumbnailer, load remote resources using an HTTP
    # client and a If-Not-Modified-Since header, etc)

    def can_handle(self, item, **params):
        return isinstance(item, File) and item.resource_type == "image"
    
    def thumbnail_changed(self, item, date):
        return date < os.stat(item.file_path).st_mtime
    
    def create_thumbnail(self, item, width, height, **params):

        image = Image.open(item.file_path)

        if width is None:
            w, h = image.size
            width = int(w * height / float(h))

        elif height is None:
            w, h = image.size
            height = int(h * width / float(w))

        image.thumbnail((width, height), self.resize_filter)

        return image


