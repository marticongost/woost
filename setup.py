#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			December 2008
"""
from setuptools import setup, find_packages
from os import listdir
from os.path import join, isdir

def rglob(base, path, patterns):
    composite = []
    for pattern in patterns:
        composite.append(join(path, pattern))
    for name in listdir(join(base, path)):
        if isdir(join(base, path, name)):
            composite.extend(rglob(base, join(path, name), patterns))
    return composite

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
    packages = find_packages(),
    package_data = {
        "woost.scripts": rglob("woost/scripts", "project_skeleton", ["*.*"]),
        "woost.views":
            ["*.cml", "*.mak"]
            + rglob("woost/views", "resources", ["*.*"])
    },
    entry_points = {
        "woost.extensions": [
            "workflow = woost.extensions.workflow:WorkflowExtension",
            "shop = woost.extensions.shop:ShopExtension",
            "countries = woost.extensions.countries:CountriesExtension",
            "payments = woost.extensions.payments:PaymentsExtension",
            "comments = woost.extensions.comments:CommentsExtension",
            "recaptcha = woost.extensions.recaptcha:ReCaptchaExtension",
            "staticsite = woost.extensions.staticsite:StaticSiteExtension",
            "sitemap = woost.extensions.sitemap:SitemapExtension",
            "pdf = woost.extensions.pdf:PDFExtension",
            "vimeo = woost.extensions.vimeo:VimeoExtension",
            "googlesearch = woost.extensions.googlesearch:GoogleSearchExtension"
        ]
    },
    # Woost can't yet access view resources (images, style sheets, client
    # side scripts, etc) that are packed inside a zipped egg, so distribution
    # in zipped form is disabled
    zip_safe = False
)

