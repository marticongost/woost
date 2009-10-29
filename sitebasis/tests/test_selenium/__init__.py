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
from cocktail.tests.seleniumtester import (
    get_selenium_enabled,
    get_selenium_site_address,
    browser
)
from sitebasis.models.initialization import init_site
from sitebasis.controllers.application import CMS

# Site defaults
admin_email = "admin@localhost"
admin_password = "topsecret"
site_languages = ("en",)

# Path for site temporary files
_site_temp_path = None

def login(user, password):
    browser.type("user", user)
    browser.type("password", password)
    browser.click("authenticate")
    browser.wait_for_page_to_load(10000)

def admin_login():
    login(admin_email, admin_password)


def setup_package():
    
    if not get_selenium_enabled():
        return

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
    cms = CMS(application_path = _site_temp_path)
    cms.run(block = False)

def teardown_package():

    if not get_selenium_enabled():
        return

    # Stop the site's webserver
    cherrypy.server.stop()
    cherrypy.engine.exit()

    # Remove temporary site files
    try:
        rmtree(_site_temp_path)
    except Exception:
        # TODO: removal of the temporary directory fails on windows, find a
        # way to make it work
        pass

