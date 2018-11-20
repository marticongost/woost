#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.events import when
from .schemanocaptchas import NoCaptcha

def add_nocaptcha(form, **member_kwargs):

    member_kwargs.setdefault("name", "nocaptcha")
    member_kwargs.setdefault("member_group", "nocaptcha")
    member = NoCaptcha(**member_kwargs)
    form.schema.add_member(member)

    if member.member_group:

        if not form.schema.groups_order:
            form.schema.groups_order = []
        elif not isinstance(form.schema.groups_order, list):
            form.schema.groups_order = list(form.schema.groups_order)

        form.schema.groups_order.append(member.member_group)

    form.adapter.exclude(member.name)
    return member

def requires_nocaptcha(form_class, **member_kwargs):

    @when(form_class.declared)
    def handler(e):
        add_nocaptcha(e.source, **member_kwargs)

    return form_class

