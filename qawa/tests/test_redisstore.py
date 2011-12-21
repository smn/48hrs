from django.test import TestCase
from qawa.redis_utils import GroupStore, UserStore
from qawa import redis_utils
from vumi.tests.utils import FakeRedis

class GroupStoreTestCase(TestCase):
    def setUp(self):
        self.msisdn = '271234567'
        self.redis = FakeRedis()
        self.user_store = UserStore(self.redis)
        self.group_store = GroupStore(self.redis)
        self.user = self.user_store.create(self.msisdn, {
            'msisdn': self.msisdn,
        })
        self.user.save()
        self.group = self.group_store.create('group-name', {
            'name': 'group-name',
        })

    def test_group_creating(self):
        self.assertTrue(self.group_store.exists('group-name'))
        self.assertIn(self.group, self.group_store.all())

    def test_group_member_adding(self):
        self.group.add_member(self.user)
        self.assertTrue(self.group.is_member(self.user))

    def test_group_member_removing(self):
        self.group.add_member(self.user)
        self.assertTrue(self.group.is_member(self.user))
        self.group.remove_member(self.user)
        self.assertFalse(self.group.is_member(self.user))

    def test_group_listing(self):
        group1 = self.group_store.create('group1', {
            'name': 'group1',
        })
        group2 = self.group_store.create('group2', {
            'name': 'group2',
        })
        self.assertIn(self.group, self.group_store.all())
        self.assertIn(group1, self.group_store.all())
        self.assertIn(group2, self.group_store.all())



class UserStoreTestCase(TestCase):

    def setUp(self):
        redis = FakeRedis()
        self.msisdn = '271234567'
        self.user_store = UserStore(redis)
        self.user_record = self.user_store.create(self.msisdn, {
            'msisdn': self.msisdn,
            'password': '123',
        })

    def test_user_record_creation(self):
        self.assertEqual(self.user_record.key, 'user:%s' % (self.msisdn,))
        self.assertEqual(self.user_record['password'], '123')

    def test_user_record_saving(self):
        self.user_record.update({'name': 'simon'})
        self.user_record.save()
        reloaded_record = self.user_record.reload()
        self.assertEqual(reloaded_record['password'], '123')
        self.assertEqual(reloaded_record['name'], 'simon')
        self.assertEqual(reloaded_record.key, 'user:%s' % (self.msisdn,))
