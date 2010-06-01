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
from woost.models import Item


class StaticSiteSnapShooter(Item):
    """A class tasked with creating a static snapshot of a site's content to
    a concrete location.
    
    This is mostly an abstract class, meant to be extended by subclasses. Each
    subclass should implement the static snapshot creation. 
    """
    instantiable = False
    visible_from_root = False
    integral = True

    destination = schema.Reference(
        type = "woost.extensions.staticsite.staticsitedestination.StaticSiteDestination",
        bidirectional = True,
        required = True,
        related_key = "snapshooter"
    )

    url = schema.String(
        required = True
    )

    @abstractmethod
    def snapshoot(self):
        """ Walks the static snapshoot of a site's content 

        @return: The file's contents, and their snapshoot's relative path. The contents can be                                                                                                                                      
        specified using a file-like object, or a filesystem path.
        @rtype: (file-like or str, str) generator
        """
    
    def __translate__(self, language, **kwargs):
        return (self.draft_source is None and self.url) \
            or Item.__translate__(self, language, **kwargs)


class WgetSnapShooter(StaticSiteSnapShooter):
    """ A class that creates a static snapshoot of a site's content using wget """
    instantiable = True

    file_names_mode = schema.String(                                          
        required = True,
        default = "unix",
        enumeration = frozenset(("unix", "windows")),
        translate_value = lambda value, **kwargs:    
            u"" if not value else translations(
                "woost.extensions.staticsite.staticsitesnapshooter.WgetSnapShooter.file_names_mode " + value,
                **kwargs
            )
    )

    def snapshoot(self):

        snapshoot_path = os.path.join(
            context["cms"].application_path,
            u"snapshoots",
            str(self.id)
        )

        cmd = "wget --mirror --page-requisites --html-extension \
            --convert-links --no-parent --no-host-directories \
            --directory-prefix=%s --restrict-file-names=%s %s"

        cmd = cmd % (snapshoot_path, self.file_names_mode, self.url)

        p = Popen(cmd, shell=True, stdout=PIPE)
        p.communicate()

        for root, dirs, files in os.walk(snapshoot_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, snapshoot_path)
                yield (file_path, relative_path)
    
