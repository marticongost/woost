#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Martí Congost <marti.congost@whads.com>
"""
from cocktail.modeling import overrides
from cocktail.translations import translations
from cocktail.controllers import get_parameter, serialize_parameter
from woost import app
from woost.models import ReadMemberPermission
from woost.models.utils import get_model_dotted_name
from .partitioningmethod import PartitioningMethod


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
        if not name:
            name = get_model_dotted_name(member.schema) + "." + member.name

        PartitioningMethod.__init__(self, name)
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

        if self.include_none_partition == "auto":
            if not self.member.required:
                yield None
        elif self.include_none_partition:
            yield None

        for value in self.__member.get_possible_values():
            yield value

    @overrides(PartitioningMethod._get_expression)
    def _get_expression(self, value):
        return self.__member.equal(value)

    @overrides(PartitioningMethod.translate_all_results)
    def translate_all_results(self):
        return (
            translations(
                self.__member,
                suffix = ".admin.partitioning.all_results"
            )
            or PartitioningMethod.translate_all_results(self)
        )

    @overrides(PartitioningMethod._translate_value)
    def _translate_value(self, value):
        return self.__member.translate_value(value)

    @overrides(PartitioningMethod._parse_value)
    def _parse_value(self, value):
        return get_parameter(
            self.__member,
            source = {self.__member.get_parameter_name(): value}.get,
            undefined = "set_none",
            implicit_booleans = False,
            errors = "raise"
        )

    @overrides(PartitioningMethod._serialize_value)
    def _serialize_value(self, value):
        return serialize_parameter(self.__member, value)


@translations.instances_of(PartitionByMember)
def _translate_partition_by_member(instance, **kwargs):
    return translations(instance.member)

