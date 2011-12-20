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
                'group': None,
                'msisdn': '+27761234567',
                'name': None,
            }))

    def test_add_to_default_group_with_name(self):
        response = ('add', {
            'group': None,
            'msisdn': '+27761234567',
            'name': 'simon'
        })
        for number in self.number_variations:
            self.assertParsedResponse('+%s simon' % (number,),
                                        response)

    def test_add_to_named_group_without_name(self):
        response = ('add', {
            'group': 'coffeelovers',
            'msisdn': '+27761234567',
            'name': None,
        })
        for number in self.number_variations:
            self.assertParsedResponse('#coffeelovers +%s' % (number,),
                                        response)

    def test_add_to_named_group_with_name(self):
        response = ('add', {
            'group': 'coffeelovers',
            'msisdn': '+27761234567',
            'name': 'simon_de_haan',
        })
        for number in self.number_variations:
            self.assertParsedResponse('#coffeelovers +%s simon_de_haan' %
                                        (number,), response)

