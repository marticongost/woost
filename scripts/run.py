#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from os.path import abspath, join, dirname
import sys
import cherrypy

src_code_path = abspath(join(dirname(abspath(__file__)), "..", ".."))

if src_code_path not in sys.path:
    sys.path.append(src_code_path)

from magicbullet.controllers import CMS
cms = CMS()
cherrypy.quickstart(cms, cms.virtual_path)

