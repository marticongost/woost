#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from setuptools import setup, find_packages

setup(
    name = "woost",
    version = "0.3",
    author = "Whads/Accent SL",
    author_email = "tech@whads.com",
    description = "An object oriented, web based Content Management System.",
    install_requires = [
        "simplejson",
        "cocktail==0.2"
    ],
    include_package_data = True,
    packages = find_packages(),
    dependency_links = ["http://www.pythonware.com/products/pil/"],   
    entry_points = {
        "woost.extensions": [
            "workflow = woost.extensions.workflow:WorkflowExtension",
            "shop = woost.extensions.shop:ShopExtension",
            "countries = woost.extensions.countries:CountriesExtension",
            "payments = woost.extensions.payments:PaymentsExtension",
            "comments = woost.extensions.comments:CommentsExtension",
            "recaptcha = woost.extensions.recaptcha:ReCaptchaExtension",
            "googlesearch = woost.extensions.googlesearch:GoogleSearchExtension"
        ]
    },
    # SiteBasis can't yet access view resources (images, style sheets, client
    # side scripts, etc) that are packed inside a zipped egg, so distribution
    # in zipped form is disabled
    zip_safe = False
)

