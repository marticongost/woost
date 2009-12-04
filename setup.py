#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from setuptools import setup, find_packages

setup(
    name = "sitebasis",
    version = "0.2",
    author = "Whads/Accent SL",
    author_email = "tech@whads.com",
    description = "An object oriented, web based Content Management System.",
    install_requires = [
        "simplejson",
        "cocktail==0.2",
        "PIL"
    ],
    include_package_data = True,
    packages = find_packages(),
    dependency_links = ["http://www.pythonware.com/products/pil/"],   
    entry_points = {
        "sitebasis.extensions": [
            "workflow = sitebasis.extensions.workflow:WorkflowExtension",
            "shop = sitebasis.extensions.shop:ShopExtension",
            "countries = sitebasis.extensions.countries:CountriesExtension",
            "payments = sitebasis.extensions.payments:PaymentsExtension",
            "comments = sitebasis.extensions.comments:CommentsExtension",
            "recaptcha = sitebasis.extensions.recaptcha:ReCaptchaExtension"
        ]
    },
    # SiteBasis can't yet access view resources (images, style sheets, client
    # side scripts, etc) that are packed inside a zipped egg, so distribution
    # in zipped form is disabled
    zip_safe = False
)

