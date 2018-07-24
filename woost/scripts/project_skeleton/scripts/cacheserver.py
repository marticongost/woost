#-*- coding: utf-8 -*-
import cherrypy
from cocktail.controllers import Controller, Dispatcher, csrfprotection
from cocktail.caching.restcacheserver import CacheController

csrfprotection.set_csrf_protection(None)

cache_server = CacheController()
cache_server.cache.storage.memory_limit = "--SETUP-CACHE_SERVER_MEMORY_LIMIT--"

if __name__ == "__main__":
    cache_server.cache.storage.verbose_invalidation = True
    cache_server.cache.storage.verbose_memory_usage = True
    cherrypy.quickstart(CacheController(), "/", {
        "global": {
            "server.socket_port": --SETUP-CACHE_SERVER_PORT--,
            "server.log_to_screen": True
        },
        "/": {
            "request.dispatch": Dispatcher()
        }
    })
else:
    application = cherrypy.tree.mount(CacheController(), "/", {
        "global": {
            "server.log_to_screen": False
        },
        "/": {
            "request.dispatch": Dispatcher()
        }
    })

