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
        reply = handler(message.user(), **payload)
        if reply:
            self.reply_to(message, reply)

    def handle_add(self, user_id, group_name, msisdn, name):
        # Get and store the user details
        group_name = group_name or DEFAULT_GROUP_NAME
        user, _ = user_store.get_or_make(msisdn)
        user['name'] = name
        user.save()

        # Update the group details
        try:
            group = group_store.find_for_user(user_id, group_name)
        except GroupStore.RecordNotFound:
            group = group_store.create_for_user(user_id, group_name)
        print group._data
        group['name'] = group_name
        group.save()
        group.add_member(msisdn)
        return '%s added to %s' % (name or msisdn, group_name)

    def handle_remove(self, user_id, group_name, msisdn):
        # Get and store the user details
        group_name = group_name or DEFAULT_GROUP_NAME
        try:
            user = user_store.find(msisdn)
            group = group_store.find_for_user(user_id, group_name)
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

    def handle_query(self, user_id, name):
        handler = getattr(self, 'handle_query_%s' % (name,), None)
        if handler:
            return handler(user_id)
        return "Not a valid query"

    # def handle_query_groups(self, user_id):
    #     groups = group_store.groups_for_user(user_id)
    #     return ' '.join(group['name'] for group in groups)

    def noop(self, user_id, **payload):
        return 'NOOP: %s -> %s' % (user_id, repr(payload),)


