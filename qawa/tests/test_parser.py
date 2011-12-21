from unittest import TestCase
from qawa.parser import QawaParser

class ParserTestCase(TestCase):

    def setUp(self):
        self.parser = QawaParser()
        self.number_variations = [
            '0761234567',
            '27761234567',
            '+27761234567',
        ]

    def assertParsedResponse(self, text, response):
        """
        Tests whether the given input results in the given
        response when parsed.
        """
        self.assertEqual(self.parser.parse(text), response)

    def tearDown(self):
        pass

    def test_add_to_default_group_without_name(self):
        for number in self.number_variations:
            self.assertParsedResponse('+%s' % (number,), ('add', {
                'group_name': '',
                'msisdn': '+27761234567',
                'name': '',
            }))

    def test_add_to_default_group_with_name(self):
        response = ('add', {
            'group_name': '',
            'msisdn': '+27761234567',
            'name': 'simon'
        })
        for number in self.number_variations:
            self.assertParsedResponse('+%s simon' % (number,),
                                        response)

    def test_add_to_default_group_with_name_and_surname(self):
        self.assertParsedResponse('+0761234567 simon de haan', ('add', {
            'group_name': '',
            'msisdn': '+27761234567',
            'name': 'simon de haan'
        }))

    def test_add_to_named_group_without_name(self):
        response = ('add', {
            'group_name': 'coffeelovers',
            'msisdn': '+27761234567',
            'name': '',
        })
        for number in self.number_variations:
            self.assertParsedResponse('#coffeelovers +%s' % (number,),
                                        response)

    def test_add_to_named_group_with_name(self):
        response = ('add', {
            'group_name': 'coffeelovers',
            'msisdn': '+27761234567',
            'name': 'simon_de_haan',
        })
        for number in self.number_variations:
            self.assertParsedResponse('#coffeelovers +%s simon_de_haan' %
                                        (number,), response)

    def test_add_to_named_group_with_name_and_surname(self):
        self.assertParsedResponse('#coffeelovers +0761234567 simon de haan', ('add', {
            'group_name': 'coffeelovers',
            'msisdn': '+27761234567',
            'name': 'simon de haan'
        }))

    def test_remove_from_group_without_name(self):
        response = ('remove', {
            'group_name': '',
            'msisdn': '+27761234567',
        })
        for number in self.number_variations:
            self.assertParsedResponse('-%s' % (number,), response)

    def test_remove_from_group_with_name(self):
        response = ('remove', {
            'group_name': 'coffeelovers',
            'msisdn': '+27761234567',
        })
        for number in self.number_variations:
            self.assertParsedResponse('#coffeelovers -%s' % (number,),
                                        response)

    def test_query(self):
        self.assertParsedResponse('?groups', ('query', {
            'name': 'groups',
        }))
        self.assertParsedResponse('?name_with_underscore', ('query', {
            'name': 'name_with_underscore',
        }))
        self.assertParsedResponse('?name_with_dash', ('query', {
            'name': 'name_with_dash',
        }))
        self.assertParsedResponse('?name-with_both', ('query', {
            'name': 'name-with_both',
        }))

    def test_find_groups(self):
        text = 'Hello #coffeelovers, grabbing coffee at #olympia'
        self.assertEqual(self.parser.find_groups(text),
                            ['coffeelovers', 'olympia'])
        text = 'something without groups'
        self.assertEqual(self.parser.find_groups(text), [])

    def test_broadcast_to_group_without_name(self):
        text = 'something without groups'
        self.assertParsedResponse(text, ('broadcast', {
            'groups': [],
            'message': text,
        }))

    def test_broadcast_to_group_with_name(self):
        text = 'Hello #coffeelovers, grabbing coffee at #olympia'
        self.assertParsedResponse(text, ('broadcast', {
            'groups': ['coffeelovers', 'olympia'],
            'message': text,
        }))
