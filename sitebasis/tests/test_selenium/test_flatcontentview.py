#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from cocktail.tests.seleniumtester import selenium_test, browser
from sitebasis.models import Item
from sitebasis.tests.test_selenium import admin_login


class FlatContentViewTestCase(object):
    
    @selenium_test
    def test_show_all(self):
        all = len(Item.select())
        browser.open("/en/cms/content/?content_view=flat&page_size=%d" % all)
        admin_login() 
        assert browser.jquery_count(".collection_display tbody tr") == all

    @selenium_test
    def test_selection_tools(self):

        browser.open("/en/cms/content/?content_view")
        admin_login()

        assert browser.is_element_present("css=.select_all")
        assert browser.is_element_present("css=.clear_selection")

        browser.click("css=.select_all")
        all = browser.jquery_count(".collection_display tbody tr")
        sel = browser.jquery_count(".collection_display tbody tr.selected")
        assert all == sel

        browser.click("css=.clear_selection")
        sel = browser.jquery_count(".collection_display tbody tr.selected")
        assert sel == 0

