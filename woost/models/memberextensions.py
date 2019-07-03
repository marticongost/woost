"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail import schema

# Add an extension property to control the default member visibility on item listings
schema.Member.listed_by_default = True
schema.Collection.listed_by_default = False
schema.CodeBlock.listed_by_default = False

# Add an extension property to indicate if members should be visible by users
schema.Member.visible = True

# Add an extension property to indicate if schemas should be instantiable by
# users
schema.Schema.instantiable = True

# Add an extension property to group types
schema.Schema.type_group = None

# Add an extension property to determine if members should participate in item
# revisions
schema.Member.versioned = True

# Extension property that allows to indicate that specific members don't modify
# the 'last_update_time' member of items when changed
schema.Member.affects_last_update_time = True

# Extension property to customize the autocomplete behavior of members
schema.SchemaObject.autocomplete_class = \
    "woost.controllers.autocomplete.CMSAutocompleteSource"
schema.Reference.autocomplete_class = \
    "woost.controllers.autocomplete.CMSAutocompleteSource"

