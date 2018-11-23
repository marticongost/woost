#-*- coding: utf-8 -*-
u"""Split results into distinct partitions (ie. tabs in backoffice listings).

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from abc import ABC, abstractmethod
from collections import OrderedDict
from cocktail.modeling import DictWrapper, overrides
from cocktail.controllers import get_parameter, serialize_parameter
from woost import app
from woost.models import ReadMemberPermission

ALL_RESULTS = object()


class Partitioning(object):
    """A partitioning scheme for an object listing, definining the distinct
    partitoning methods that can be applied to it.

    Partitioning schemes are typically used by setting the
    `woost.admin.sections.crud.CRUD.partitioning` property.
    """

    parameter_separator = "-"

    def __init__(self, *methods):
        """Initializes the partitioning scheme, adding the indicated
        methods.

        :param methods: An arbitrary number of methods to add to the scheme.
        :type methods: `PartitioningMethod`
        """
        self.__methods = OrderedDict()
        for method in methods:
            self.add_method(method)

    @property
    def methods(self):
        """A read only mapping with all the methods supported by this
        partitioning scheme.
        """
        return DictWrapper(self.__methods)

    def add_method(self, method):
        """Adds a new partitioning method to the scheme."""
        self.__methods[method.name] = method

    def available_methods(self):
        """Produces an iterator containing all the partitioning methods of the
        scheme that can apply to the current context.
        """
        for method in self.__methods.itervalues():
            if method.is_available():
                yield method

    def parse_parameter(self, parameter_value):
        """Resolves a partitioning method and a partition value from the given
        from a serialized string.

        :return: A partitioning method and a partition value.
        :rtype: tuple of `PartitioningMethod`, object
        """
        pos = parameter_value.find(self.parameter_separator)
        if pos == -1:
            raise ValueError("Invalid partition parameter: " + parameter_value)

        method_name = parameter_value[:pos]
        value_str = parameter_value[pos + 1:]

        method = self.__methods[method_name]
        value = method.parse_value(value_str)

        return method, value

    def serialize_parameter(self, method, value):
        """Serializes a partitioning method and a partition value into a single
        string.

        :parameter method: The partitioning method to serialize.
        :type method: `PartitioningMethod`

        :parameter value: The partition value to serialize.

        :return: The serialized value.
        :rtype: str
        """
        return "%s%s%s" % (
            method.name,
            self.parameter_separator,
            method.serialize_value(value)
        )


class PartitioningMethod(ABC):
    """A specific partitioning method for an object listing.

    This is an abstract base class;

    .. attribute:: include_all_results_partition

        A boolean indicating wether to include a partition matching all
        results.
    """

    enabled = True
    include_all_results_partition = True
    all_results_identifier = "_all_"

    def __init__(self, name):
        self.__name = name

    @property
    def name(self):
        """The name that uniquely identifies the partitioning method in the
        partitioning scheme it belongs to.

        Used to index methods in the `Partitioning.methods` property, and to
        select the active partitioning method through a query string parameter
        (see `Partitioning.parse_parameter` and
        `Partitioning.serialize_parameter`).
        """
        return self.__name

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
    def values(self):
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

        :parameter value: The partition to translate.
        :type value: object

        :return: The translation for the partition.
        :rtype: str
        """
        if value is ALL_RESULTS:
            return translations("woost.admin.partitioning.ALL_RESULTS")
        else:
            return self._translate_value(value)

    @abstractmethod
    def _translate_value(self, value):
        """A method that must be implemented by subclasses in order to obtain
        the human readable description for the given partition.

        :parameter value: The partition to translate.
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

        :parameter value: The value to deserialize.
        :type value: str

        :return: A value representing a single partition of this method.
        :rtype: object
        """
        if value == self.all_results_identifier:
            return ALL_RESULTS
        else:
            return self._parse_value(self, value)

    @abstractmethod
    def _parse_value(self, value):
        """A method that must be implemented by subclasses in order to
        deserialize values identifying specific partitions.

        :parameter value: The value to deserialize.
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

        :parameter value: The value to serialize.
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

        :parameter value: The value to serialize.
        :type value: object

        :return: The serialized value.
        :rtype: object
        """
        raise TypeError(
            "%s doesn't implement its serialize_value() method"
            % self.__class__
        )


class PartitionByMember(PartitioningMethod):
    """A partitioning method based on a single member of a listing.

    .. attribute:: include_none_partition

        Whether to generate a separate partition for None values. Can take any
        of the following values:

            - True: generate a partition matching None values
            - False: don't generate the partition
            - "auto": only generate the partition if the member is not
              required (this is the default)
    """

    include_none_partition = "auto"

    def __init__(
        self,
        member,
        name = None,
        include_none_partition = None,
        **kwargs
    ):
        """Initializes the partitioning method, specifying the member that sets
        up the partitions.

        :param member: The member used to determine the available partitions.
        :type member: `cocktail.schema.member.Member`

        :param name: The name that will be given to this partitioning method.
            Defaults to the member name.
        :type name: str

        :param include_none_partition: Whether to include a separate partition for None
            values (see the `include_none_partition` attribute).
        :type include_none_partition: bool
        """
        PartitioningMethod.__init__(self, name or member.name)
        self.__member = member

        if include_none_partition is not None:
            self.include_none_partition = include_none_partition

    @property
    def member(self):
        """The member partitioned by this method."""
        return self.__member

    @overrides(PartitioningMethod.is_available)
    def is_available(self):
        return (
            PartitioningMethod.is_available(self)
            and app.user.has_permission(
                ReadMemberPermission,
                member = self.__member
            )
        )

    @overrides(PartitioningMethod._values)
    def _values(self):

        if self.include_none_partition:
            yield None

        for value in self.__member.get_possible_values():
            yield value

    @overrides(PartitioningMethod._get_expression)
    def _get_expression(self, value):
        return self.__member.equal(value)

    @overrides(PartitioningMethod._translate_value)
    def _translate_value(self, value):
        return self.__member.translate_value(value)

    @overrides(PartitioningMethod._parse_value)
    def _parse_value(self, value):
        return get_parameter(
            self.__member,
            source = {self.__member.parameter_name: value}.get,
            undefined = "set_none",
            implicit_booleans = False,
            errors = "raise"
        )

    @overrides(PartitioningMethod._serialize_value)
    def _serialize_value(self, value):
        return serialize_parameter(self.__member, value)

