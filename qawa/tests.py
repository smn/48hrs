from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

class ApiTestCase(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_authentication(self):
        resp = self.client.get(reverse('home'))
        self.assertTrue(resp.status_code, 403)
        
        resp = self.client.post(reverse('home'), {'username': 'test', 'password': 'test'})
        self.assertTrue(resp.status_code, 200)
        
        resp = self.client.get(reverse('home'))
        self.assertTrue(resp.status_code, 200)