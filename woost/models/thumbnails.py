#-*- coding: utf-8 -*-
"""
Provides classes that generate thumbnail images for CMS items.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			April 2009
"""
import os
import re
import datetime
import commands
from time import mktime
import Image
from subprocess import Popen, PIPE
from shutil import rmtree
from tempfile import mkdtemp
from cocktail.modeling import abstractmethod
from woost.models import File


class ThumbnailLoader(object):
    """A class that produces thumbnail images for content items.
    
    @var cache_path: A directory used to store copies of generated
        thumbnails, to speed up further thumbnail requests for the same item.
        Clearing this attribute disables thumbnail caching.
    @type cache_path: str

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
        @type item: L{Item<woost.models.Item>}

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
        thumbnailer = None,
        **params):
        """Gets the path to the file where thumbnails for the given request
        will be stored.
        
        @param item: The item represented by the thumbnail.
        @type item: L{Item<woost.models.Item>}

        @param width: The width (in pixels) of the generated thumbnail.
        @type width: int

        @param height: The height (in pixels) of the generated thumbnail.
        @type height: int

        @param thumbnailer: The thumbnailer used by the loader to generate the 
            thumbnails. 
        @type thumbnailer: L{thumbnailer<Thumbnailer>}

        @param params: A set of formatting options that should be observed by
            the thumbnailer.
        
        @return: The path for the requested thumbnail.
        @rtype: str
        """
        item, width, height = self._sanitize_request(item, width, height)

        if thumbnailer is None:
            thumbnailer = self.get_thumbnailer(item, **params)

        if thumbnailer is None:
            return None

        # Base name
        file_name = "%s-%sx%s" % (item.id, width or "auto", height or "auto")

        # Parameters
        param_list = "-".join(
            "%s:%s" % (key, value)
            for key, value in params.iteritems()
            if key in thumbnailer.relevant_cache_parameters
        )    
        if param_list:
            file_name += "-" + param_list

        # File format
        file_format = params.get("format", self.default_format)
        if file_format:
            file_name += "." + file_format

        return os.path.join(self.cache_path, file_name)

    def get_thumbnail(self, item,
        width = None,
        height = None,
        thumbnailer = None,
        **params):
        """Gets a thumbnail image for the given item.

        @param item: The item to create the thumbnail for.
        @type item: L{Item<woost.models.Item>}

        @param width: The width (in pixels) of the generated thumbnail.
        @type width: int

        @param height: The height (in pixels) of the generated thumbnail.
        @type height: int

        @param thumbnailer: The thumbnailer used by the loader to generate the 
            thumbnails. 
        @type thumbnailer: L{thumbnailer<Thumbnailer>}

        @param params: A set of formatting options that should be observed by
            the thumbnailer.

        @return: The generated thumbnail.
        @rtype: L{Image<Image.Image>}
        """
        item, width, height = self._sanitize_request(item, width, height)
        
        if thumbnailer is None:
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
                thumbnailer,
                **params
            )

            # Make sure cached thumbnails are current
            if cached_thumbnail_path and os.path.exists(cached_thumbnail_path):
                thumbnail_date = os.stat(cached_thumbnail_path).st_mtime
                if thumbnailer.get_last_change_in_source(item) > thumbnail_date:
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
    """Thumbnailers generate thumbnail images for certain kinds of items.

    @param relevant_cache_parameters: A set listing which thumbnail parameters
        to take into account when deciding the file name for cached copies of
        generated thumbnails.
    @type relevant_cache_parameters: str set

    """
    resize_filter = Image.ANTIALIAS
    relevant_cache_parameters = frozenset()

    @abstractmethod
    def can_handle(self, item, **params):
        """Indicates if the thumbnailer can generate the requested thumbnail.

        @param item: The item to create the thumbnail for.
        @type item: L{Item<woost.models.Item>}
        
        @param params: A set of formatting options that should be observed by
            the thumbnailer. Thumbnailers are free to decide they are not
            capable of generating a thumbnail if a particular option is set to
            an unsupported value.

        @return: True if the thumbnailer can generate the requested thumbnail,
            False otherwise.
        @rtype: bool
        """

    def get_request_parameters(self, width, height, **kwargs):
        """Gets the parameters passed to the thumbnailer
        
        @param width: The width (in pixels) of the generated thumbnail.
        @type width: int

        @param height: The height (in pixels) of the generated thumbnail.
        @type height: int

        @param params: A set of formatting options that should be observed by
            the thumbnailer.
        """

        if width is not None:
            width = int(width)

        if height is not None:
            height = int(height)
        
        params = {}

        quality = kwargs.get("quality")
        if quality is not None:	    
            params["quality"] = int(quality)

        optimize = kwargs.get("optimize")
        if optimize is not None:
            params["optimize"] = (optimize == "true")

        progressive = kwargs.get("progressive")
        if progressive is not None:
            params["progressive"] = (progressive == "progressive")

        return width, height, params
    
    def get_last_change_in_source(self, item):
        """Indicates the last time the item was modified in a way that may
        alter its resulting thumbnail.
        
        This method is used by L{thumbnail loaders<ThumbnailLoader>} to
        decide which cached thumbnails should be ditched and created anew.

        @param item: The item to test.
        @type item: L{Item<woost.models.Item>}

        @return: A timestamp indicating the last known change to the item's
            state that can affect its resulting thumbnail.
        @rtype: float
        """
        return mktime(item.last_update_time.timetuple())

    @abstractmethod
    def create_thumbnail(self, item, width, height, **params):
        """Creates a thumbnail image for the given item.

        @param item: The item to create the thumbnail for.
        @type item: L{Item<woost.models.Item>}

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

    # TODO: Extend it to any publishable with resource_type == "image", loading
    # their produced image using an HTTP client

    def can_handle(self, item, **params):
        return isinstance(item, File) and item.resource_type == "image"
    
    def get_last_change_in_source(self, item):
        return os.stat(item.file_path).st_mtime
    
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

class VideoThumbnailer(Thumbnailer):
    """Generates thumbnails for video files."""

    relevant_cache_parameters = frozenset(["position"])
    try:
        p = Popen(["which", "ffmpeg"], stdout=PIPE)
        ffmpeg_path = p.communicate()[0].replace("\n", "") or None
    except:
        ffmpeg_path = None


    def _secs2time(self, s):
        ms = int((s - int(s)) * 1000000)
        s = int(s)
        # Get rid of this line if s will never exceed 86400
        while s >= 24*60*60: s -= 24*60*60
        h = s / (60*60)
        s -= h*60*60
        m = s / 60
        s -= m*60
        return datetime.time(h, m, s, ms)
    
    def _time2secs(self, d):
        return d.hour*60*60 + d.minute*60 + d.second + \
            (float(d.microsecond) / 1000000)

    def can_handle(self, item, **params):
        return self.ffmpeg_path and isinstance(item, File) \
            and item.resource_type == "video"
    
    def get_request_parameters(self, width, height, **kwargs):
        
        width, height, params = Thumbnailer.get_request_parameters(
            self, width, height, **kwargs
        )

        position = kwargs.get("position")
        if position is not None:
            params["position"] = int(position)

        return width, height, params

    def get_last_change_in_source(self, item):
        return os.stat(item.file_path).st_mtime
    
    def create_thumbnail(self, item, width, height, **params):

        duration = commands.getoutput(
            u"%s -i %s 2>&1 | grep \"Duration\" | cut -d ' ' -f 4 | sed s/,//" % (
                self.ffmpeg_path, 
                item.file_path
            )
        )
        duration_list = re.split("[\.:]", duration)
        video_length = datetime.time(
            int(duration_list[0]), int(duration_list[1]),
            int(duration_list[2]), int(duration_list[3])
        )
    
        if "position" in params:
            position = params.get("position")
            time = self._secs2time(position)
        else:
            seconds = self._time2secs(video_length)
            time = self._secs2time(seconds / 2)
    
        if time > video_length:
            raise ThumbnailParameterError(
                "Must specify a smaller position than the video duration."
            )
    
        temp_dir = mkdtemp()
        temp_image = os.path.join(temp_dir, unicode(item.id))
        grabimage = u"%s -y -i %s -vframes 1 -ss %s -an -vcodec png -f rawvideo %s " % (
            self.ffmpeg_path, item.file_path, time.strftime("%H:%M:%S"), temp_image
        )
    
        grab = commands.getoutput(grabimage)
    
        image = Image.open(temp_image)

        rmtree(temp_dir)
    
        if width is None:
                w, h = image.size
                width = int(w * height / float(h))
    
        elif height is None:
            w, h = image.size
            height = int(h * width / float(w))
    
        image.thumbnail((width, height), self.resize_filter)
    
        return image
