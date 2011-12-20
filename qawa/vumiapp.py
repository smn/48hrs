from twisted.python import log
from vumi.application import ApplicationWorker
from qawa.parser import QawaParser, QawaSyntaxError
from qawa.redis_utils import UserStore, GroupStore
from vumi.tests.utils import FakeRedis

parser = QawaParser()
redis = FakeRedis()
user_store = UserStore(redis)
group_store = GroupStore(redis)
DEFAULT_GROUP_NAME = 'my-group'

class QawaApplication(ApplicationWorker):

    def consume_user_message(self, message):
        try:
            action, payload = parser.parse(message['content'])
        except QawaSyntaxError:
            log.err()
            self.reply_to(message, 'syntax error in %s' % (message['content'],))

        handler = getattr(self, 'handle_%s' % (action,), self.noop)
        reply = handler(**payload)
        if reply:
            self.reply_to(message, reply)

    def handle_add(self, group_name, msisdn, name):
        # Get and store the user details
        group_name = group_name or DEFAULT_GROUP_NAME
        user, _ = user_store.get_or_make(msisdn)
        if name:
            user['name'] = name
        user.save()
        # Update the group details
        group, _ = group_store.get_or_make(group_name)
        group.save()
        group.add_member(msisdn)
        return '%s added to %s' % (name or msisdn, group_name)

    def handle_remove(self, group_name, msisdn):
        # Get and store the user details
        group_name = group_name or DEFAULT_GROUP_NAME
        try:
            user = user_store.find(msisdn)
            group = group_store.find(group_name)
            if group.is_member(msisdn):
                group.remove_member(msisdn)
                return '%s removed from %s' % (user.get('name', msisdn), group_name)
            else:
                return '%s not a member of %s' % (user.get('name', msisdn), group_name)
        except UserStore.RecordNotFound:
            log.err()
            return 'User %s not found' % (msisdn,)
        except GroupStore.RecordNotFound:
            log.err()
            return 'Group %s not found' % (group_name,)

    # def handle_

    def noop(self, **payload):
        return 'NOOP: %s' % (repr(payload),)


