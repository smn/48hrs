from unittest import TestCase
from qawa.parser import QawaParser

class ParserTestCase(TestCase):

    def setUp(self):
        self.parser = QawaParser()

    def assertParsedResponse(self, text, response):
        self.assertEqual(self.parser.parse(text), response)

    def tearDown(self):
        pass

    def test_add_to_default_group(self):
        self.assertParsedResponse('+0761234567', ('add', {
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
        self.assertParsedResponse('+0761234567 simon', response)
        self.assertParsedResponse('+27761234567 simon', response)
        self.assertParsedResponse('++27761234567 simon', response)
