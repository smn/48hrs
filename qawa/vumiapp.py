from vumi.application import ApplicationWorker

class QawaApplication(ApplicationWorker):
    
    def consume_user_message(self, message):
        self.reply_to(message, 'you said %s' % (message['content'],))
    


