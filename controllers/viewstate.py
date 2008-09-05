#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			September 2008
"""
import cherrypy
from cgi import parse_qs
from urllib import urlencode, quote

def get_state(**kwargs):
    state = parse_qs(cherrypy.request.query_string)
    state.update(kwargs)
    
    for key, value in state.items():
        if value is None:
            del state[key]

    return state

def view_state(**kwargs):
    return urlencode(get_state(**kwargs), True)

def view_state_form(**kwargs):

    form = []

    for key, values in get_state(**kwargs).iteritems():
        if values is not None:
            for value in values:
                form.append(
                    "<input type='hidden' name='%s' value='%s'>"
                    % (key, quote(value))
                )

    return "\n".join(form)

