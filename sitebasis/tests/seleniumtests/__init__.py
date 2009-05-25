#-*- coding: utf-8 -*-
"""
Selenium test suite for the SiteBasis CMS.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from os.path import join        
from shutil import rmtree
from tempfile import mkdtemp
from ZODB.FileStorage import FileStorage
import cherrypy
from cocktail.persistence import datastore
from cocktail.tests.seleniumtester import get_selenium_site_address
from sitebasis.models.initialization import init_site
from sitebasis.tests.seleniumtests.sitedefaults import (
    admin_email,
    admin_password,
    site_languages
)
from sitebasis.tests.seleniumtests.test_authentication import (
    AuthenticationTestCase
)

_db_path = None

# To be set by the invoking test suite
_site_launcher = None
_site_launcher_args = ()
_site_launcher_kwargs = {}

def set_site_launcher(launcher, *args, **kwargs):
    global _site_launcher, _site_launcher_args, _site_launcher_kwargs
    _site_launcher = launcher
    _site_launcher_args = args
    _site_launcher_kwargs = kwargs

def setup_package():

    # Set up a temporary database
    global _dp_path
    _dp_path = mkdtemp()
    datastore.storage = FileStorage(join(_dp_path, "testdb.fs"))

    # Initialize site content before testing
    init_site(
        admin_email,
        admin_password,
        site_languages
    )
    datastore.commit()

    # Configure the site's webserver
    hostname, port = get_selenium_site_address()
    cherrypy.config.update({
        "log.screen": False,
        "server.socket_host": hostname,
        "server.socket_port": port,
        "engine.autoreload.on": False
    })

    # Launch the site's webserver on another thread
    _site_launcher(*_site_launcher_args, **_site_launcher_kwargs)

def teardown_package():
    
    # Stop the site's webserver
    cherrypy.server.stop()
    cherrypy.engine.exit()

    # Discard the temporary database
    datastore.abort()
    datastore.close()
    rmtree(_dp_path)

