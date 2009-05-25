#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			May 2009
"""
from cocktail.tests.seleniumtester import selenium_test, browser
from sitebasis.models import Item
from sitebasis.tests.test_selenium.sitedefaults import (
    admin_email,
    admin_password
)


class FlatContentViewTestCase(object):

    def load_view(self, url = "/en/cms/?content_view=flat"):
        browser.open(url)
        browser.type("user", admin_email)
        browser.type("password", admin_password)
        browser.click("authenticate")
        browser.wait_for_page_to_load(10000)

    @selenium_test
    def test_show_all(self):

        all = len(Item.select())

        self.load_view(
            "/en/cms/"
            "?content_view=flat"
            "&page_size=" + str(all)
        )

        assert browser.jquery_count(".collection_display tbody tr") == all

    @selenium_test
    def test_selection_tools(self):

        self.load_view()

        assert browser.is_element_present("css=.select_all")
        assert browser.is_element_present("css=.clear_selection")

        browser.click("css=.select_all")
        all = browser.jquery_count(".collection_display tbody tr")
        sel = browser.jquery_count(".collection_display tbody tr.selected")
        assert all == sel

        browser.click("css=.clear_selection")
        sel = browser.jquery_count(".collection_display tbody tr.selected")
        assert sel == 0

