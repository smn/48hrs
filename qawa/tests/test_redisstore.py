from unittest import TestCase
from qawa.redis_utils import GroupStore, UserStore
from qawa import redis_utils
from vumi.tests.utils import FakeRedis

class GroupStoreTestCase(TestCase):
    def setUp(self):
        self.msisdn = '271234567'
        self.redis = FakeRedis()
        self.user_store = UserStore(self.redis)
        self.group_store = GroupStore(self.redis)
        self.user, _ = self.user_store.get_or_make(self.msisdn)
        self.user.save()
        self.group, _ = self.group_store.get_or_make('group-name')

    def test_group_member_adding(self):
        self.group.add_member(self.msisdn)
        self.assertIn(self.user.key, [user.key for user in
                                            self.group.members()])

    def test_group_member_removing(self):
        self.group.add_member(self.msisdn)
        self.assertIn(self.user.key, [user.key for user in
                                            self.group.members()])
        self.group.remove_member(self.msisdn)
        self.assertNotIn(self.user.key, [user.key for user in
                                            self.group.members()])



class UserStoreTestCase(TestCase):

    def setUp(self):
        redis = FakeRedis()
        self.user_store = UserStore(redis)
        self.msisdn = '271234567'

    def test_user_record_creation(self):
        user_record = self.user_store.create(self.msisdn, {'password': '123'})
        self.assertEqual(user_record.key, 'user:%s' % (self.msisdn,))
        self.assertEqual(user_record['password'], '123')

    def test_user_record_saving(self):
        user_record = self.user_store.create(self.msisdn, {'password': '123'})
        user_record.update({'name': 'simon'})
        user_record.save()
        reloaded_record = user_record.reload()
        self.assertEqual(reloaded_record['password'], '123')
        self.assertEqual(reloaded_record['name'], 'simon')
        self.assertEqual(reloaded_record.key, 'user:%s' % (self.msisdn,))
