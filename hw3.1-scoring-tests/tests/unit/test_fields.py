from datetime import datetime
import unittest

import api
from ..utils import cases


class TestCharField(unittest.TestCase):
    def setUp(self):
        self.field = api.CharField()

    @cases(['some text', ''])
    def test_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases([12312, {}, []])
    def test_invalid_type(self, value):
        self.assertRaises(TypeError, self.field.validate, value)

    @cases(['some text', None, []])
    def test_to_python(self, value):
        self.assertEqual(self.field.to_python(value), value)


class TestArgumentsField(unittest.TestCase):
    def setUp(self):
        self.field = api.ArgumentsField()

    @cases([{'k': 123}, {}])
    def test_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases(['str', 12312, []])
    def test_invalid_type(self, value):
        self.assertRaises(TypeError, self.field.validate, value)


class TestEmailField(TestCharField):
    def setUp(self):
        self.field = api.EmailField()

    @cases(['user1@mail.ru'])
    def test_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases([12312, {}, []])
    def test_invalid_type(self, value):
        self.assertRaises(TypeError, self.field.validate, value)

    @cases(['some text', ''])
    def test_invalid_format(self, value):
        self.assertRaises(TypeError, self.field.validate, value)


class TestPhoneField(unittest.TestCase):
    def setUp(self):
        self.field = api.PhoneField()

    @cases([71234567890, '71234567890'])
    def test_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases([12.312, {}, []])
    def test_invalid_type(self, value):
        self.assertRaises(TypeError, self.field.validate, value)

    @cases([7123456, '7123456789012345'])
    def test_invalid_length(self, value):
        self.assertRaises(ValueError, self.field.validate, value)

    @cases([91234567890, '51234567890', 'abcdefghijk'])
    def test_invalid_first_char(self, value):
        self.assertRaises(ValueError, self.field.validate, value)


class TestDateField(unittest.TestCase):
    def setUp(self):
        self.field = api.DateField()

    @cases(['01.01.2019'])
    def test_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases([12312, {}, []])
    def test_invalid_type(self, value):
        self.assertRaises(TypeError, self.field.validate, value)

    @cases(['01012019', '40.01.2019'])
    def test_invalid_format(self, value):
        self.assertRaises(ValueError, self.field.validate, value)

    @cases([
        ['01.01.2019', datetime(2019, 1, 1)],
        ['01012019', '01012019'],
    ])
    def test_to_python(self, value):
        self.assertEqual(self.field.to_python(value[0]), value[1])


class TestBirthDayField(unittest.TestCase):
    def setUp(self):
        self.field = api.BirthDayField()

    @cases(['01.01.2019'])
    def test_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases([12312, {}, []])
    def test_invalid_type(self, value):
        self.assertRaises(TypeError, self.field.validate, value)

    @cases(['01012019', '40.01.2019'])
    def test_invalid_format(self, value):
        self.assertRaises(ValueError, self.field.validate, value)

    @cases(['01.01.1910', '01.01.2040'])
    def test_invalid_age(self, value):
        self.assertRaises(ValueError, self.field.validate, value)


class TestGenderField(unittest.TestCase):
    def setUp(self):
        self.field = api.GenderField()

    @cases([0, 1, 2])
    def test_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases(['some text', 12.312, {}, []])
    def test_invalid_type(self, value):
        self.assertRaises(TypeError, self.field.validate, value)

    @cases([-1, 3, 1000])
    def test_invalid_value(self, value):
        self.assertRaises(ValueError, self.field.validate, value)


if __name__ == '__main__':
    unittest.main()
