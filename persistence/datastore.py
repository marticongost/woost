#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from threading import local
from ZODB import FileStorage, DB
import transaction
from magicbullet.modeling import getter

class DataStore(object):

    def __init__(self, storage):
        self._thread_data = local()
        self.storage = storage
        self.db = DB(storage)

    @getter
    def root(self):
        
        root = getattr(self._thread_data, "root", None)

        if root is None:
            self._thread_data.root = root = self.connection.root()

        return root

    @getter
    def connection(self):

        connection = getattr(self._thread_data, "connection", None)

        if connection is None:
            self._thread_data.connection = connection = self.db.open()

        return connection

    commit = transaction.commit
    abort = transaction.abort

    def close(self):

        if hasattr(self._thread_data, "root"):
            del self._thread_data.root

        if hasattr(self._thread_data, "connection"):
            self._thread_data.connection.close()
            del self._thread_data.connection

