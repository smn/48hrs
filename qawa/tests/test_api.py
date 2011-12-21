from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from vumi.tests.utils import FakeRedis
from qawa import views
from qawa.redis_utils import UserStore, GroupStore

class ApiTestCase(TestCase):
    def setUp(self):
        fake_redis = FakeRedis()
        views.user_store = UserStore(fake_redis)
        views.group_store = GroupStore(fake_redis)
        self.client = Client()

    def test_authentication(self):
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

        usr = views.user_store.register('0123456789','test')
        
        resp = self.client.post(reverse('auth'), {'username': '0123456789', 'password': 'test'})
        self.assertContains(resp, '"auth": true')

        resp = self.client.get(reverse('home'))
        self.assertTrue(resp.status_code, 200)

        resp = self.client.get(reverse('auth'))
        self.assertContains(resp, '"auth": true')

    def test_register_view(self):
        resp = self.client.get(reverse('register'))
        self.assertTrue(resp.status_code, 501)

        resp = self.client.post(reverse('register'), {'username': '0123456789'})
        self.assertContains(resp, '"auth": true')
        
        usr = views.user_store.register('0123456789','test')

        resp = self.client.post(reverse('register'), {'username': '0123456789'})
        self.assertContains(resp, 'Username is already taken.')
        
    def test_groups_view(self):
        resp = self.client.get(reverse('groups'))
        self.assertTrue(resp.status_code, 403)
        
        usr = views.user_store.register('0123456789','test')
        
        resp = self.client.post(reverse('auth'), {'username': '0123456789', 'password': 'test'})

        resp = self.client.get(reverse('groups'))
        self.assertContains(resp, '[]')

        resp = self.client.post(reverse('groups'), {'name': 'coffee lovers'})
        self.assertTrue(resp.status_code, 201)
        
        resp = self.client.post(reverse('groups'), {'name': 'coffee lovers'})
        self.assertTrue(resp.status_code, 400)

    def test_messages_view(self):
        resp = self.client.get(reverse('messages'))
        self.assertTrue(resp.status_code, 403)
        
        usr = views.user_store.register('0123456789','test')
        
        resp = self.client.post(reverse('auth'), {'username': '0123456789', 'password': 'test'})

        resp = self.client.get(reverse('messages'))
        self.assertContains(resp, '[]')

        resp = self.client.post(reverse('messages'), {'group': 'coffee lovers', 'message': 'hello world!'})
        self.assertTrue(resp.status_code, 201)

    def test_live_view(self):
        resp = self.client.get(reverse('live'), {'channel': 'coffee lovers'})
        #self.assertTrue(resp.status_code, 403)
        
        usr = views.user_store.register('0123456789','test')
        
        resp = self.client.post(reverse('auth'), {'username': '0123456789', 'password': 'test'})

        resp = self.client.get(reverse('live'), {'channel': 'coffee lovers'})
        self.assertTrue(resp.status_code, 200)
        
        resp = self.client.get(reverse('live'))
        self.assertTrue(resp.status_code, 400)
