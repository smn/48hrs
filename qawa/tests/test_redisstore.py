from unittest import TestCase
from qawa.redis_utils import RedisStore, UserStore
from vumi.tests.utils import FakeRedis

class UserStoreTestCase(TestCase):

    def setUp(self):
        self.store = UserStore(FakeRedis)

    def test_user_record_creation(self):
        user_record = self.store.create('123', {'password': '123'})
        self.assertEqual(user_record.key, 'user:123')
        self.assertEqual(user_record['password'], '123')

    def test_user_record_saving(self):
        user_record = self.store.create('123', {'password': '123'})
        user_record.update({'name': 'simon'})
        user_record.save()
        reloaded_record = user_record.reload()
        self.assertEqual(reloaded_record['password'], '123')
        self.assertEqual(reloaded_record['name'], 'simon')
        self.assertEqual(reloaded_record.key, 'user:123')
