from twisted.internet.defer import inlineCallbacks, returnValue
from vumi.application.tests.test_base import ApplicationTestCase
from vumi.tests.utils import FakeRedis
from qawa.redis_utils import UserStore, GroupStore
from qawa.vumiapp import QawaApplication, DEFAULT_GROUP_NAME
from qawa import vumiapp

class VumiappTestCase(ApplicationTestCase):

    application_class = QawaApplication
    msisdn = '27123456789'
    other_msisdn = '27123456790'

    def setUp(self):
        super(VumiappTestCase, self).setUp()
        fake_redis = FakeRedis()
        vumiapp.user_store = UserStore(fake_redis)
        vumiapp.group_store = GroupStore(fake_redis)

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
        self.assertEqual(response['content'], '+%s not a member of coffeelovers' % (self.msisdn, ))
