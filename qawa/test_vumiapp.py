from twisted.internet.defer import inlineCallbacks, returnValue
from vumi.application.tests.test_base import ApplicationTestCase
from qawa.vumiapp import QawaApplication, DEFAULT_GROUP_NAME

class VumiappTestCase(ApplicationTestCase):

    application_class = QawaApplication
    msisdn = '27123456789'

    @inlineCallbacks
    def fake_incoming(self, content):
        application = yield self.get_application({})
        msg = self.mkmsg_in(content=content)
        # submit a message to the application
        self.dispatch(msg)
        # check the application's response
        [msg] = yield self.wait_for_dispatched_messages(1)
        returnValue(msg)

    @inlineCallbacks
    def test_add_to_default_group(self):
        msg = yield self.fake_incoming('+%s' % (self.msisdn,))
        self.assertEqual(msg['content'], '+%s added to %s' %
                            (self.msisdn, DEFAULT_GROUP_NAME))

    @inlineCallbacks
    def test_add_to_named_group(self):
        msg = yield self.fake_incoming('#coffeelovers +%s' % (self.msisdn,))
        self.assertEqual(msg['content'], '+%s added to %s' %
                            (self.msisdn, 'coffeelovers'))

    @inlineCallbacks
    def test_remove_from_default_group(self):
        msg = yield self.fake_incoming('-%s' % (self.msisdn,))
        self.assertEqual(msg['content'], '+%s removed from %s' %
                            (self.msisdn, DEFAULT_GROUP_NAME))

    @inlineCallbacks
    def test_remove_from_named_group(self):
        msg = yield self.fake_incoming('#coffeelovers -%s' % (self.msisdn,))
        self.assertEqual(msg['content'], '+%s removed from %s' %
                            (self.msisdn, 'coffeelovers'))
