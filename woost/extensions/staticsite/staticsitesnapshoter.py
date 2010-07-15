#-*- coding: utf-8 -*-
"""

@author:		Jordi Fernández
@contact:		jordi.fernandez@whads.com
@organization:	Whads/Accent SL
@since:			March 2010
"""
import os
from subprocess import Popen, PIPE
from cocktail import schema
from cocktail.controllers import context
from cocktail.modeling import abstractmethod
from cocktail.translations import translations
from cocktail.controllers.location import Location
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

    @abstractmethod
    def snapshot(self, root, follow_links = True):
        """ Generates the snapshot of a site's content 

        @param root: The item which the exportation will statrt.
        @type root: Publishable

        @param follow_links: Indicates if the exportantion will follow links.
        @type follow_links: bool
        """

    @abstractmethod
    def files(self):
        """ Walks the static snapshot of a site's content 

        @return: The file's contents, and their snapshot's relative path. The contents can be                                                                                                                                      
        specified using a file-like object, or a filesystem path.
        @rtype: (file-like or str, str) generator
        """
    

class WgetSnapShoter(StaticSiteSnapShoter):
    """ A class that creates a static snapshot of a site's content using wget """
    instantiable = True

    file_names_mode = schema.String(                                          
        required = True,
        default = "unix",
        enumeration = frozenset(("unix", "windows")),
        translate_value = lambda value, **kwargs:    
            u"" if not value else translations(
                "woost.extensions.staticsite.staticsitesnapshoter.WgetSnapShoter.file_names_mode " + value,
                **kwargs
            )
    )

    def snapshot(self, root, follow_links = True):
        snapshot_path = os.path.join(
            context["cms"].application_path,
            u"snapshots",
            str(self.id)
        )

        cmd = "wget --mirror"

        if not follow_links:
            cmd += " --level 1"

        cmd += " --page-requisites --html-extension \
                --convert-links --no-parent --no-host-directories \
                --directory-prefix=%s --restrict-file-names=%s %s"

        location = Location.get_current_host()                              
        location.path_info = context["cms"].uri(root)
        cmd = cmd % (
            snapshot_path, 
            self.file_names_mode, 
            unicode(location).encode("utf-8")
        )

        p = Popen(cmd, shell=True, stdout=PIPE)
        p.communicate()

    def files(self):
        snapshot_path = os.path.join(
            context["cms"].application_path,
            u"snapshots",
            str(self.id)
        )

        for root, dirs, files in os.walk(snapshot_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, snapshot_path)
                yield (file_path, relative_path)
    
