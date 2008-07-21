#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from threading import local
from ZODB import DB
import transaction
from magicbullet import settings
from magicbullet.modeling import getter

class DataStore(object):
    """A thread safe wrapper over the application's object database. Normally
    used through its global L{datastore} instance.
    
    The class expects an X{storage} setting, containing a
    L{storage<ZODB.BaseStorage.BaseStorage>} instance pointing to the physical
    location of the database (see the ZODB documentation for more details).
    """

    def __init__(self, storage):
        self._thread_data = local()
        self.storage = storage
        self.db = DB(storage)

    @getter
    def root(self):
        """Gives access to the root container of the database. The property is
        thread safe; accessing it on different threads will produce different
        containers, each bound to a separate database connection.
        @type: mapping 
        """
        root = getattr(self._thread_data, "root", None)

        if root is None:
            self._thread_data.root = root = self.connection.root()

        return root

    @getter
    def connection(self):
        """Returns the database connection for the current thread. The property
        is thread safe; accessing it on different threads will produce
        different connections. Once called, each connection remains bound to a
        single thread until the thread finishes or the datastore's L{close}
        method is called.
        @type: L{Connection<ZODB.Connection.Connection>}
        """
        connection = getattr(self._thread_data, "connection", None)

        if connection is None:
            self._thread_data.connection = connection = self.db.open()

        return connection

    commit = transaction.commit
    abort = transaction.abort

    def close(self):
        """Closes the connection to the database for the current thread.
        Accessing the L{root} or L{connection} properties after this method is
        called will spawn a new database connection.
        """
        if hasattr(self._thread_data, "root"):
            del self._thread_data.root

        if hasattr(self._thread_data, "connection"):
            self._thread_data.connection.close()
            del self._thread_data.connection


datastore = DataStore(settings.storage)

