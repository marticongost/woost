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
    def test_sort_by_id(self):
        
        browser.open(
            "/en/cms/content/?content_view=flat"
            "&page_size=%d"
            "&members=element&members=id"   
            % len(Item.select())
        )
        admin_login()

        def get_browser_ids():
            return browser.get_eval(
                "var ids = [];"
                "window.jQuery('.collection_display tbody td.id_column')"
                ".each(function () {"
                "   ids.push(window.jQuery(this).text());"
                "});"
                "ids.join(' ');"
            )

        # Show the column dropdown panel and click the ascending order button
        browser.click("css=.collection_display th.id_column .selector a.label")
        browser.click(
            "css=.collection_display th.id_column .sorting_options "
            "a.ascending"
        )
        browser.wait_for_page_to_load(10000)
        sorted_ids = " ".join(str(x.id) for x in Item.select(order = "id"))
        print sorted_ids
        print get_browser_ids()
        assert get_browser_ids() == sorted_ids

        # Show the column dropdown panel and click the descending order button
        browser.click("css=.collection_display th.id_column .selector a.label")
        browser.click(
            "css=.collection_display th.id_column .sorting_options "
            "a.descending"
        )
        browser.wait_for_page_to_load(10000)
        sorted_ids = " ".join(str(x.id) for x in Item.select(order = "-id"))
        assert get_browser_ids() == sorted_ids

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

