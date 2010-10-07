#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from time import time
from simplejson import loads
from urllib import urlopen
from cocktail.iteration import first
from cocktail.events import event_handler
from cocktail.translations import translations
from cocktail import schema
from cocktail.persistence import datastore
from woost.models import Extension

translations.define("LocationsExtension",
    ca = u"Localitats",
    es = u"Localidad",
    en = u"Locations"
)

translations.define("LocationsExtension.update_frequency",
    ca = u"Freqüència d'actualització",
    es = u"Frecuencia de actualización",
    en = u"Update frequency"
)

translations.define("LocationsExtension.update_frequency-explanation",
    ca = u"El nombre de dies entre actualitzacions de la llista de localitats",
    es = u"El número de días entre actualizaciones de la lista de localidades",
    en = u"Number of days between updates to the list of locations"
)

SECONDS_IN_A_DAY = 60 * 60 * 24


class LocationsExtension(Extension):

    def __init__(self, **values):
        Extension.__init__(self, **values)
        self.extension_author = u"Whads/Accent SL"
        self.set("description",
            u"""Proporciona accés a la llista de països del món i les seves
            regions, actualitzada a través d'Internet.""",
            "ca"
        )
        self.set("description",            
            u"""Proporciona acceso a la lista de países del mundo y sus
            regiones, actualizada a través de Internet.""",
            "es"
        )
        self.set("description",
            u"""Provides a list of world countries and their regions, 
            automatically updated from the Internet.""",
            "en"
        )

    last_update = None

    service_uri = "http://services.woost.info/locations"

    update_frequency = schema.Integer(
        min = 1,
        required = True,
        default = 15
    )

    @event_handler
    def handle_loading(cls, event):
        
        from woost.extensions.locations import location, strings

        now = time()
        ext = event.source

        if ext.last_update is None \
        or now - ext.last_update >= ext.update_frequency * SECONDS_IN_A_DAY:
            ext.sync_locations()
            ext.last_update = now
            datastore.commit()

    def sync_locations(self):
        
        from woost.extensions.locations.location import Location
        
        text_data = urlopen(self.service_uri).read()
        json_data = loads(text_data)

        def process_record(record, parent = None):

            code = record["code"]
            
            if parent: 
                location = first(
                    child
                    for child in parent.locations
                    if child.code == code
                )
            else:
                location = first(Location.select([
                    Location.parent.equal(None),
                    Location.code.equal(code)
                ]))

            if location is None:
                location = Location()
                location.parent = parent
                location.code = code
                location.insert()

            for lang, value in record["name"].iteritems():
                if isinstance(value, str):
                    value = value.decode("utf-8")
                location.set("location_name", value, lang)

            children = record.get("locations")
            if children:
                for child_record in children:
                    process_record(child_record, location)

            return location

        for record in json_data:
            process_record(record)

