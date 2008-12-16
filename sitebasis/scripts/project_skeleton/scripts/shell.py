#-*- coding: utf-8 -*-
"""A convenience script that can be launched through ipython or vanilla python
with the -i flag, to have quick access to the project's data.
"""
from __future__ import with_statement
from cocktail.language import *
from cocktail.translations import *
from cocktail.persistence import *
from sitebasis.models import *
import _PROJECT_MODULE_

DEFAULT_LANGUAGE = "en"
set_language(DEFAULT_LANGUAGE)
set_content_language(DEFAULT_LANGUAGE)

