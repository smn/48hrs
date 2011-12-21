from twisted.internet.defer import inlineCallbacks
from vumi.application.tests.test_base import ApplicationTestCase
from qawa.vumiapp import QawaApplication

class VumiappTestCase(ApplicationTestCase):

    application_class = QawaApplication

    @inlineCallbacks
    def test_something(self):
        application = yield self.get_application({})
        print application
