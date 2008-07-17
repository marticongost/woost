#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from magicbullet import settings
from magicbullet.persistence.datastore import DataStore
from magicbullet.persistence.incremental_id import IncrementalIdGenerator

datastore = DataStore(settings.storage)

_id_generator = IncrementalIdGenerator()

def incremental_id():
    return _id_generator.generate_id(datastore.root)

if __name__ == "__main__":
 
    from threading import Thread

    running = True

    class GenerateIdsThread(Thread):
        def run(self):
            while running:
                print self.getName(), incremental_id()

    for i in range(10):
        thread = GenerateIdsThread()
        thread.setName("thread-" + str(i))
        thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        running = False

    datastore.commit()
    datastore.close()

