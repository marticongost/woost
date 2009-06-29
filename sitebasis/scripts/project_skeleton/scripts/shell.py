#!/usr/bin/env python
#-*- coding: utf-8 -*-
u"""A convenience script that can be launched through ipython or vanilla python
with the -i flag, to have quick access to the project's data.
"""
from __future__ import with_statement
from cocktail.language import *
from cocktail.translations import *
from cocktail.persistence import *
from sitebasis.models import *
from sitebasis.models.extension import load_extensions
from _PROJECT_MODULE_.models import *

site = Site.main
rules = site.access_rules_by_priority

DEFAULT_LANGUAGE = site.default_language
set_language(DEFAULT_LANGUAGE)
set_content_language(DEFAULT_LANGUAGE)
load_extensions()

