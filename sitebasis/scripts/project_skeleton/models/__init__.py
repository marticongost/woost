#-*- coding: utf-8 -*-
u"""
Site specific models.
"""
from sitebasis.models import Template
Template.engine.default = "_TEMPLATE_ENGINE_"
del Template

