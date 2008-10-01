#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			August 2008
"""
# Object store provider
from ZEO.ClientStorage import ClientStorage
storage = ClientStorage(("127.0.0.1", 2008))

# Application server configuration
server_config = {
    "global": {
        "server.socket_host": "192.168.0.56",
        "tools.encode.on": True,
        "tools.encode.encoding": "utf-8",
        "tools.decode.on": True,
        "tools.decode.encoding": 'utf-8'
    }
}

# Back office view settings are preserved on a cookie. This setting establishes
# the maximum time span during which these settings will be remembered. Takes
# the same values as the 'max-age' cookie parameter (so setting it to -1 will
# drop the settings as soon the browser is closed, and 0 won't preserve view
# settings at all).
back_office_settings_duration = 60 * 60 * 24 * 30 # ~= 1 month

