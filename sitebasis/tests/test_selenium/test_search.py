#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2009
"""
from __future__ import with_statement
from contextlib import contextmanager
from cocktail.tests.seleniumtester import selenium_test, browser
from sitebasis.models import Item
from sitebasis.tests.test_selenium import admin_login

@contextmanager
def override(obj, **kwargs):

    undefined = object()

    prev_values = {}
    
    try:
        for key, value in kwargs.iteritems():
            prev_values[key] = getattr(obj, key, undefined)
            setattr(obj, key, value)
    
        yield

    finally:
        for key, value in prev_values.iteritems():
            if value is undefined:
                delattr(obj, key)
            else:
                setattr(obj, key, value)


class SearchTestCase(object):
    
    @selenium_test
    def test_unfold_expanded_search(self):
        browser.open("/en/cms/content/?content_view=flat")
        admin_login()
        browser.click("css=.advanced_search")
        browser.wait_for_page_to_load(10000)
        assert browser.is_element_present("css=.filters")
        assert browser.is_element_present("css=.filters .new_filter_selector")

    @selenium_test
    def test_add_filters_from_selector(self):
        
        from cocktail.schema.expressions import GlobalSearchExpression
        from cocktail.persistence import Query
        
        results = Item.select([
            Item.id.greater(15),
            GlobalSearchExpression("@localhost", "en")
        ])        
        results_count = len(results)

        browser.open(
            "/en/cms/content/?content_view=flat&search_expanded=true"
            "&page_size=%d" % (results_count + 1)
        )
        admin_login()

        # Add filters
        for i, filter_id in enumerate(("member-id", "global_search")):
            browser.fire_event("css=.new_filter_selector", "click")
            browser.fire_event("css=.new_filter-%s" % filter_id, "click")

        assert browser.jquery_count(".filters .filter_list .filter_entry") == 2
        print "-" * 80
        print browser.jquery_count(".collection_display .item_row")
        print "-" * 80

        # Set values on filters
        browser.type("filter_operator0", "gt")
        browser.type("filter_value0", "15")
        browser.type("filter_value1", "@localhost")
        browser.click("css=.filters .search_button")
        browser.wait_for_page_to_load(10000)

        # Test the returned content
        rows_count = browser.jquery_count(".collection_display .item_row")
        assert rows_count == results_count

        # Supplied values must be preserved between page loads
        assert browser.get_selected_value("filter_operator0") == "gt"
        assert browser.get_value("filter_value0") == "15"
        assert browser.get_value("filter_value1") == "@localhost"

