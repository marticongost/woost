#-*- coding: utf-8 -*-
"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from abc import ABCMeta, abstractmethod
from cocktail.translations import translations
from .registration import _methods

ALL_RESULTS = object()


class PartitioningMethod(object, metaclass=ABCMeta):
    """A specific partitioning method for an object listing.

    This is an abstract base class. Most partitioning will be based on a single
    schema member, which is offered by the
    `~woost.admin.partitioning.PartitionByMember` subclass. More unusual
    partitioning schemes might need to extend this class to implement their
    partitioning criteria.

    .. attribute:: include_all_results_partition

        A boolean indicating whether to include a partition matching all
        results.

    .. attribute:: enabled

        A boolean indicating whether the method is enabled or not. Disabled
        methods are not shown on the admin interface.
    """

    enabled = True
    include_all_results_partition = True
    all_results_identifier = "_all_"

    def __init__(self, name):
        self.__name = name
        _methods[name] = self

    @property
    def name(self):
        """The name that uniquely identifies the partitioning method throughout
        the admin.

        Used to retrieve methods by name through `get_method`, and to select
        the active partitioning method through a query string parameter
        (see `parse_partition_parameter` and `serialize_partition_parameter`).
        """
        return self.__name

    def export_data(self):
        """Export the data required by the admin UI.

        :return: A javascript serializable object.
        :rtype: object
        """
        return {
            "name": self.__name,
            "label": translations(self)
        }

    def is_available(self):
        """Indicates if this partitioning method should be eligible in the
        current context.

        :return: A boolean
        """
        return self.enabled

    def values(self):
        """Produces an iterator containing all the possible values for this
        partition method.

        :return: An iterable sequence of values representing the specific
            partitions for this method.
        :rtype: iterable
        """
        if self.include_all_results_partition:
            yield ALL_RESULTS

        for value in self._values():
            yield value

    @abstractmethod
    def _values(self):
        """A method that must be implemented by subclasses in order to produce
        all the possible values for this partition method.

        :return: An iterable sequence of values representing the specific
            partitions for this method.
        :rtype: iterable
        """
        raise TypeError(
            "%s doesn't implement its _values() method"
            % self.__class__
        )

    def get_expression(self, value):
        """Gets the filter expression that should be applied to a query to
        obtain the results for the given partition.

        :param value: A partition value.
        :type value: object

        :return: A filter expression representing the given partition, or None
            if the chosen partition represents the whole result set.
        :rtype: `cocktail.schema.expressions.Expression`
        """
        if value is ALL_RESULTS:
            return None
        else:
            return self._get_expression(value)

    @abstractmethod
    def _get_expression(self, value):
        """A method that must be implemented by subclasses in order to resolve
        the filter expression for a given partition value.

        :param value: A value representing a specific partition.
        :type value: object

        :return: The expression matching the given filter.
        :rtype: `cocktail.schema.expressions.Expression`
        """
        raise TypeError(
            "%s doesn't implement its _get_expression() method"
            % self.__class__
        )

    def translate_value(self, value):
        """Obtains the human readable description for the given partition.

        :param value: The partition to translate.
        :type value: object

        :return: The translation for the partition.
        :rtype: str
        """
        if value is ALL_RESULTS:
            return self.translate_all_results()
        else:
            return self._translate_value(value)

    def translate_all_results(self):
        """Obtains the human readable description for the partition
        representing all values.

        :return: The translation for the 'all results' partition.
        :rtype: str
        """
        return translations("woost.admin.partitioning.all_results")

    @abstractmethod
    def _translate_value(self, value):
        """A method that must be implemented by subclasses in order to obtain
        the human readable description for the given partition.

        :param value: The partition to translate.
        :type value: object

        :return: The translation for the partition.
        :rtype: str
        """
        raise TypeError(
            "%s doesn't implement its _translate_value() method"
            % self.__class__
        )

    def parse_value(self, value):
        """Deserializes a partition value.

        :param value: The value to deserialize.
        :type value: str

        :return: A value representing a single partition of this method.
        :rtype: object
        """
        if value == self.all_results_identifier:
            return ALL_RESULTS
        else:
            return self._parse_value(value)

    @abstractmethod
    def _parse_value(self, value):
        """A method that must be implemented by subclasses in order to
        deserialize values identifying specific partitions.

        :param value: The value to deserialize.
        :type value: str

        :return: A value representing a single partition of this method.
        :rtype: object
        """
        raise TypeError(
            "%s doesn't implement its _parse_value() method"
            % self.__class__
        )

    def serialize_value(self, value):
        """Serializes a partition value.

        :param value: The value to serialize.
        :type value: object

        :return: The serialized value.
        :rtype: object
        """
        if value == ALL_RESULTS:
            return self.all_results_identifier
        else:
            return self._serialize_value(value)

    @abstractmethod
    def _serialize_value(self, value):
        """A method that must be implemented by subclasses in order to
        serialize values identifying specific partitions.

        :param value: The value to serialize.
        :type value: object

        :return: The serialized value.
        :rtype: object
        """
        raise TypeError(
            "%s doesn't implement its serialize_value() method"
            % self.__class__
        )

    def partition_query(self, query, selected_value):
        """Applies the partitioning method to the given query.

        :param query: The query to partition.
        :type query: `cocktail.persistence.Query`

        :param selected_value: The partition to select; will be used to
            filter the query.
        :type selected_value: object

        :return: A tuple containing the filtered query and a sequence of
            partition values and their result counts.
        :rtype: (`cocktail.persistence.Query`, (object, int) iterable)
        """
        selected_partition_query = None
        result_counts = []

        for value in list(self.values()):

            partition_expr = self.get_expression(value)

            if partition_expr is None:
                partition_query = query
            else:
                partition_query = query.select()
                partition_query.add_filter(partition_expr)

            result_counts.append((value, len(partition_query)))

            if value == selected_value:
                selected_partition_query = partition_query

        if selected_partition_query is None:
            raise ValueError("Invalid partition value: %r" % selected_value)

        return selected_partition_query, result_counts

