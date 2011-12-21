# -*- test-case-name: qawa.test_vumiapp -*-
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
        try:
            user = user_store.find(msisdn)
            user['name'] = name
            user.save()
        except UserStore.RecordNotFound:
            user = user_store.create(msisdn, {
                'name': name,
                'msisdn': msisdn,
            })

        # Update the group details
        user.join_group(group_name)
        return '%s added to %s' % (name or msisdn, group_name)

    def handle_remove(self, user_id, group_name, msisdn):
        # Get and store the user details
        group_name = group_name or DEFAULT_GROUP_NAME
        try:
            user = user_store.find(msisdn)
            group = group_store.find(group_name)
            if group.is_member(user):
                user.leave_group(group_name)
                return '%s removed from %s' % (
                            user.get('name') or msisdn, group_name)
            else:
                return '%s not a member of %s' % (
                            user.get('name') or msisdn, group_name)
        except UserStore.RecordNotFound:
            return 'User %s not found' % (msisdn,)
        except GroupStore.RecordNotFound:
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


