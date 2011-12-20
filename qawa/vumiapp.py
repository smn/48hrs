from twisted.python import log
from vumi.application import ApplicationWorker
from qawa.parser import QawaParser, QawaSyntaxError
from qawa.redis_utils import UserStore, GroupStore

parser = QawaParser()
DEFAULT_GROUP_NAME = 'my-group'

store = RedisStore()

class QawaApplication(ApplicationWorker):

    def consume_user_message(self, message):
        try:
            action, payload = parser.parse(message['content'])
        except QawaSyntaxError:
            log.err()
            self.reply_to(message, 'syntax error in %s' % (message['content'],))

        handler = getattr(self, 'handle_%s' % (action,), self.noop)
        handler(message, **payload)

    def handle_add(self, message, group, msisdn, name):
        if not group:
            group = DEFAULT_GROUP_NAME
        store.add_to_group(group, msisdn, name)
        self.reply_to(message, 'adding %s' % (payload,))

    def noop(self, message, **payload):
        self.reply_to(message, 'NOOP: "%s" parsed as "%s"' %
                                (message['content'], payload))


