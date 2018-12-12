#-*- coding: utf-8 -*-
u"""Split results into distinct partitions (ie. tabs in backoffice listings).

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.translations import translations
from .registration import (
    get_method,
    require_method,
    register_method,
    methods,
    available_methods
)
from .serialization import (
    parse_partition_parameter,
    serialize_partition_parameter
)
from .partitioningmethod import PartitioningMethod, ALL_RESULTS
from .partitionbymember import PartitionByMember

translations.load_bundle("woost.admin.partitioning.package")

