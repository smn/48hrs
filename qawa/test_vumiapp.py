from twisted.internet.defer import inlineCallbacks, returnValue
from vumi.application.tests.test_base import ApplicationTestCase
from vumi.tests.utils import FakeRedis
from vumi.utils import normalize_msisdn
from qawa.redis_utils import UserStore, GroupStore, MessageStore
from qawa.vumiapp import QawaApplication, DEFAULT_GROUP_NAME
from qawa import vumiapp

def normalize(msisdn):
    return normalize_msisdn(msisdn, country_code='27')

class VumiappTestCase(ApplicationTestCase):

    application_class = QawaApplication
    msisdn = '27123456789'
    other_msisdn = '27123456790'

    def setUp(self):
        super(VumiappTestCase, self).setUp()
        fake_redis = FakeRedis()
        vumiapp.user_store = self.user_store = UserStore(fake_redis)
        vumiapp.group_store = self.group_store = GroupStore(fake_redis)
        vumiapp.message_store = self.message_store = MessageStore(fake_redis)

    @inlineCallbacks
    def fake_incoming(self, content):
        application = yield self.get_application({})
        msg = self.mkmsg_in(content=content)
        # submit a message to the application
        self.dispatch(msg)

    @inlineCallbacks
    def test_add_and_remove_from_default_group(self):
        yield self.fake_incoming('+%s' % (self.msisdn,))
        yield self.fake_incoming('-%s' % (self.msisdn,))
        [response1, response2] = yield self.wait_for_dispatched_messages(2)

        self.assertEqual(response1['content'], '+%s added to %s' %
                            (self.msisdn, DEFAULT_GROUP_NAME))
        self.assertEqual(response2['content'], '+%s removed from %s' %
                            (self.msisdn, DEFAULT_GROUP_NAME))

    @inlineCallbacks
    def test_add_and_remove_from_named_group(self):
        yield self.fake_incoming('#coffeelovers +%s' % (self.msisdn,))
        yield self.fake_incoming('#coffeelovers -%s' % (self.msisdn,))
        [response1, response2] = yield self.wait_for_dispatched_messages(2)
        self.assertEqual(response1['content'], '+%s added to %s' %
                            (self.msisdn, 'coffeelovers'))
        self.assertEqual(response2['content'], '+%s removed from %s' %
                            (self.msisdn, 'coffeelovers'))

    @inlineCallbacks
    def test_remove_from_named_group_without_membership(self):
        yield self.fake_incoming('+%s' % (self.msisdn,))
        yield self.fake_incoming('#coffeelovers +%s' % (self.other_msisdn,))
        yield self.fake_incoming('#coffeelovers -%s' % (self.msisdn,))
        [_, _, response] = yield self.wait_for_dispatched_messages(1)
        self.assertEqual(response['content'],
            '+%s not a member of coffeelovers' % (self.msisdn, ))

    @inlineCallbacks
    def test_remove_from_unknown_group(self):
        yield self.fake_incoming('+%s' % (self.msisdn,))
        yield self.fake_incoming('#unknown-group -%s' % (self.msisdn,))
        [_, response] = yield self.wait_for_dispatched_messages(2)
        self.assertEqual(response['content'],
            'Group unknown-group not found')

    @inlineCallbacks
    def test_remove_unknown_user(self):
        yield self.fake_incoming('-%s' % (self.msisdn,))
        [response] = yield self.wait_for_dispatched_messages(1)
        self.assertEqual(response['content'],
            'User +%s not found' % (self.msisdn,))

    @inlineCallbacks
    def test_broadcast_to_default_group(self):
        yield self.fake_incoming('+%s' % (self.msisdn,))
        yield self.fake_incoming('+%s' % (self.other_msisdn,))
        yield self.fake_incoming('hello world!')
        responses = yield self.wait_for_dispatched_messages(2)
        messages = self.message_store.get_messages(DEFAULT_GROUP_NAME)
        [message1, message2] = messages
        self.assertEqual(message1[0]['message'], 'hello world!')
        self.assertEqual(message1[0]['author'], '+%s' % (self.msisdn,))
        self.assertEqual(message2[0]['message'], 'hello world!')
        self.assertEqual(message2[0]['author'], '+%s' % (self.other_msisdn,))

        user_message1 = self.message_store.get_live_messages(
                            normalize(self.msisdn), DEFAULT_GROUP_NAME)
        self.assertEqual(user_message1, message1)

        user_message2 = self.message_store.get_live_messages(
                            normalize(self.other_msisdn), DEFAULT_GROUP_NAME)
        self.assertEqual(user_message2, message2)
