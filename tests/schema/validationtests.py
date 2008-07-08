#-*- coding: utf-8 -*-
"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			March 2008
"""

from unittest import TestCase

class ValidationTestCase(TestCase):

    def _test_validation(
        self,
        member,
        correct_values,
        incorrect_values,
        error_type,
        error_attributes = None,
        error_count = 1):

        from magicbullet.schema import Schema      

        for value in correct_values:
            assert member.validate(value), \
                "%r is a valid value" % value
            assert not list(member.get_errors(value))

        for value in incorrect_values:            
            assert not member.validate(value), \
                "%r is not a valid value" % value
            errors = list(member.get_errors(value))
            assert len(errors) == error_count
            error = errors[0]
            assert isinstance(error, error_type), \
                "%r is an instance of %r" % (error, error_type)
            #assert error.member is member
            
            if error_attributes:
                for attrib_key, attrib_value in error_attributes.iteritems():
                    assert getattr(error, attrib_key) == attrib_value

class MemberValidationTestCase(ValidationTestCase):
    
    def test_required(self):

        from magicbullet.schema import Member, ValueRequiredError

        self._test_validation(
            Member(required = True),
            [1, 0, -2, "a", "hello world!!", "", [], {}],
            [None],
            ValueRequiredError
        )

    def test_require_none(self):

        from magicbullet.schema import Member, NoneRequiredError

        self._test_validation(
            Member(require_none = True),
            [None],
            [1, 0, -2, "a", "hello world!!", "", [], {}],
            NoneRequiredError
        )

    def test_type(self):

        from magicbullet.schema import Member, TypeCheckError

        self._test_validation(
            Member(type = basestring),
            [None, "hello world", u"Hola món!", ""],
            [15, 0, [], ["hello world"], {}],
            TypeCheckError,
            {"type": basestring}
        )

        self._test_validation(
            Member(type = float),
            [None, 1.5, 27.104, 12.8],
            ["", "hello!", 2, {}, [1.5, 27.3]],
            TypeCheckError,
            {"type": float}
        )

    def test_enumeration(self):

        from magicbullet.schema import Member, EnumerationError

        self._test_validation(
            Member(enumeration = ["cherry", "apple", "peach"]),            
            [None, "cherry", "apple", "peach"],
            ["coconut", "watermelon", "banana"],
            EnumerationError
        )
    
class StringValidationTestCase(ValidationTestCase):

    def test_min(self):

        from magicbullet.schema import String, MinLengthError

        self._test_validation(
            String(min = 5),
            [None, "hello", "strange", ", strange world!!"],
            ["", "hulo", "hum"],
            MinLengthError
        )

    def test_max(self):
        
        from magicbullet.schema import String, MaxLengthError

        self._test_validation(
            String(max = 5),
            [None, "", "hi", "hulo", "hello"],
            ["greetings", "welcome"],
            MaxLengthError
        )

    def test_format(self):

        from magicbullet.schema import String, FormatError

        self._test_validation(
            String(format = r"^\d{4}-\d{2}[a-zA-Z]$"),
            [None, "4261-85M", "7508-34x"],
            ["", "Bugger numeric codes", "AAADSADS20934832498234"],
            FormatError
        )

class IntegerValidationTestCase(ValidationTestCase):

    def test_min(self):

        from magicbullet.schema import Integer, MinValueError

        self._test_validation(
            Integer(min = 5),
            [None, 5, 6, 15, 300],
            [4, 3, 0, -2, -100],
            MinValueError
        )    

    def test_max(self):

        from magicbullet.schema import Integer, MaxValueError

        self._test_validation(
            Integer(max = 5),
            [None, 5, 4, 0, -6, -78],
            [6, 7, 15, 100, 300],
            MaxValueError
        )

class CollectionValidationTestCase(ValidationTestCase):

    def test_min(self):
        
        from magicbullet.schema import Collection, MinItemsError

        self._test_validation(
            Collection(min = 3),
            [None, [1, 2, 3], ["a", "b", "c", "d"], range(50)],
            [[], ["a"], [1, 2]],
            MinItemsError
        )

    def test_max(self):

        from magicbullet.schema import Collection, MaxItemsError

        self._test_validation(
            Collection(max = 3),
            [None, [], ["a"], (1, 2), set([1, 2, 3])],
            [["a", "b", "c", "d"], range(10)],
            MaxItemsError
        )

    def test_content(self):

        from magicbullet.schema import Collection, Integer, TypeCheckError

        self._test_validation(
            Collection(content = Integer()),
            [None, [], [1], [1, 2], set([1, 2, 3]), tuple(range(10))],
            [["a", "b", "c"], [3.5, 2.7, 1.4]],
            TypeCheckError,
            error_count = 3
        )

class SchemaValidationTestCase(ValidationTestCase):

    def test_scalar(self):

        from magicbullet.schema import Schema, Integer, TypeCheckError
        
        class Validable(object):
            def __init__(self, foo):
                self.foo = foo

            def __repr__(self):
                return "Validable(%r)" % self.foo

        self._test_validation(
            Schema(members = {
                "foo": Integer()
            }),
            [Validable(None), Validable(1), Validable(15)],
            [Validable(""), Validable("hello, world!"), Validable(3.15)],
            TypeCheckError
        )

if __name__ == "__main__":
    from unittest import main
    main()

