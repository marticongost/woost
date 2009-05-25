#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			October 2008
"""

# Application server configuration
import cherrypy
cherrypy.config.update({
    "global": {
        "server.socket_host": "_WEBSERVER_HOST_",
        "server.socket_port": _WEBSERVER_PORT_,
        "tools.encode.on": True,
        "tools.encode.encoding": "utf-8",
        "tools.decode.on": True,
        "tools.decode.encoding": 'utf-8'
    }
})

# Object store provider
from cocktail.persistence import datastore
from ZEO.ClientStorage import ClientStorage
db_host = "_DATABASE_HOST_"
db_port = _DATABASE_PORT_
datastore.storage = lambda: ClientStorage((db_host, db_port))
