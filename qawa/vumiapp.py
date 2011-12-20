from twisted.python import log
from vumi.application import ApplicationWorker
from qawa.parser import QawaParser, QawaSyntaxError

parser = QawaParser()

class QawaApplication(ApplicationWorker):

    def consume_user_message(self, message):
        try:
            response = parser.parse(message['content'])
            self.reply_to(message, 'parsed response %s' % (repr(response),))
        except QawaSyntaxError:
            log.err()
            self.reply_to(message, 'syntax error in %s' % (message['content'],))



