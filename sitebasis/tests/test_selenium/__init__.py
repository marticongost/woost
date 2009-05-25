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
from sitebasis.controllers.application import CMS
from sitebasis.tests.test_selenium.sitedefaults import (
    admin_email,
    admin_password,
    site_languages
)

# Path for site temporary files
_site_temp_path = None

def setup_package():

    # Create a temporary folder to hold site files
    global _site_temp_path
    _site_temp_path = mkdtemp()

    # Set up a temporary database
    datastore.storage = FileStorage(join(_site_temp_path, "testdb.fs"))

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
    cms = CMS()
    cms.application_path = _site_temp_path
    cms.run(block = False)

def teardown_package():
    
    # Stop the site's webserver
    cherrypy.server.stop()
    cherrypy.engine.exit()

    # Remove temporary site files
    rmtree(_site_temp_path)

