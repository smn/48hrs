from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from vumi.tests.utils import FakeRedis
from qawa import views
from qawa.redis_utils import RedisStore

class ApiTestCase(TestCase):
    def setUp(self):
        views.r_store = RedisStore(FakeRedis)
        self.client = Client()
    
    def test_authentication(self):
        resp = self.client.get(reverse('home'))
        self.assertTrue(resp.status_code, 403)
        
        resp = self.client.get(reverse('auth'))
        self.assertTrue(resp.status_code, 403)
        
        resp = self.client.post(reverse('auth'), {'username': 'test', 'password': 'test'})
        self.assertContains(resp, 'Please enter a valid phone number')
        
        resp = self.client.post(reverse('auth'), {'username': '0124', 'password': 'test'})
        self.assertContains(resp, 'Please enter a valid phone number')
        
        resp = self.client.post(reverse('auth'), {'username': '+27124', 'password': 'test'})
        self.assertContains(resp, 'Please enter a valid phone number')
        
        resp = self.client.post(reverse('auth'), {'username': '0123456789', 'password': 'test'})
        self.assertContains(resp, 'Cannot authenticate user.')
        
        resp = self.client.get(reverse('register'))
        self.assertTrue(resp.status_code, 501)
        
        resp = self.client.post(reverse('register'), {'username': '0123456789'})
        self.assertContains(resp, '"auth": true')
        
        views.r_store.register('0123456789','test')
        
        resp = self.client.post(reverse('register'), {'username': '0123456789'})
        self.assertContains(resp, 'Username is already taken.')
        
        resp = self.client.post(reverse('auth'), {'username': '0123456789', 'password': 'test'})
        self.assertContains(resp, '"auth": true')
        
        resp = self.client.get(reverse('home'))
        self.assertTrue(resp.status_code, 200)
        
        resp = self.client.get(reverse('auth'))
        self.assertContains(resp, '"auth": true')