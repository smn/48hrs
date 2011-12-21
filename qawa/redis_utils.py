import redis

class RedisStoreException(Exception): pass
class RecordNotFound(RedisStoreException): pass

class RedisRecord(object):
    """
    Base record for storing stuff in Redis. All data is
    mapped to a Redis hash.
    """

    def __init__(self, store, key, **data):
        self.store = store
        self.key = key
        self._data = data

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def get(self, key, default=None):
        return self._data.get(key, default)

    def items(self):
        return self._data.items()

    def update(self, data):
        self._data.update(data)
        return self._data

    def save(self):
        self.store.save_dict(self.key, self._data)

    def __eq__(self, other):
        return self.key == other.key

    def reload(self):
        return self.store.make_record(self.key, self.store.read_dict(self.key))

class RedisStore(object):
    """
    A store for managing the storage and retrieval of data from Redis.
    This must be subclassed as each store is be responsible for generating
    their own unique key with the `generate_key()` function.

    If `record_class` is provided then that class will be used to create
    the records with. Whatever it is, it must subclass or duck-type the
    base `RecordClass`.
    """

    record_class = RedisRecord

    def __init__(self, redis):
        self.r_server = redis
        exception_class_name = '%sRecordNotFound' % (self.__class__.__name__,)
        self.index_key = self.generate_key('/index')
        self.__class__.RecordNotFound = type(exception_class_name,
                                            (RecordNotFound,), {})

    def generate_key(self, key):
        raise RedisStoreException('Please override the generate_key() function')

    def key_exists(self, key):
        return self.r_server.exists(key)

    def exists(self, pk):
        return self.key_exists(self.generate_key(pk))

    def make_record(self, key, data):
        return self.record_class(self, key, **data)

    def save_dict(self, key, data):
        self.r_server.hmset(key, data)

    def read_dict(self, key):
        return self.r_server.hgetall(key)

    def add_to_set(self, key, data):
        self.r_server.sadd(key, data)

    def remove_from_set(self, key, data):
        self.r_server.srem(key, data)

    def set_members(self, key):
        return self.r_server.smembers(key)

    def create(self, pk, data):
        key = self.generate_key(pk)
        record = self.make_record(key, data)
        record.save()
        self.add_to_set(self.index_key, pk)
        return record

    def get_or_make(self, pk):
        key = self.generate_key(pk)
        try:
            return self.find(key), False
        except self.RecordNotFound:
            return self.make_record(key, {}), True

    def find(self, pk):
        key = self.generate_key(pk)
        if self.key_exists(key):
            data = self.read_dict(key)
            record = self.make_record(key, data)
            return record
        raise self.RecordNotFound('Cannot find record with key %s' % (repr(key),))

    def all(self):
        pks = self.set_members(self.index_key)
        return [self.find(pk) for pk in pks]


class UserStoreRecord(RedisRecord):
    def __init__(self, *args, **kwargs):
        super(UserStoreRecord, self).__init__(*args, **kwargs)
        self.groups_key = '%s:groups' % (self.key,)
        self.group_store = GroupStore(self.store.r_server)

    def join_group(self, group_name):
        try:
            group = self.group_store.find(group_name)
        except GroupStore.RecordNotFound:
            group = self.group_store.create(group_name, {
                'name': group_name,
            })
        group.add_member(self)
        self.store.add_to_set(self.groups_key, group_name)

    def leave_group(self, group_name):
        group = self.group_store.find(group_name)
        group.remove_member(self)
        self.store.remove_from_set(self.groups_key, group_name)


class UserStore(RedisStore):

    record_class = UserStoreRecord

    def generate_key(self, msisdn):
        return 'user:%s' % (msisdn,)

    def authenticate(self, username, password):
        user = self.read_dict(self.generate_key(username))
        return user and user.get('password') == password

    def register(self, username, password):
        return self.create(username, {'password': password})

    def user_exists(self, username):
        return self.key_exists(self.generate_key(username))

class GroupStoreRecord(RedisRecord):

    def __init__(self, *args, **kwargs):
        super(GroupStoreRecord, self).__init__(*args, **kwargs)
        self.members_key = '%s:members' % (self.key,)
        self.user_store = UserStore(self.store.r_server)

    def add_member(self, user_record):
        self.store.add_to_set(self.members_key, user_record['msisdn'])

    def members(self):
        return [self.user_store.find(msisdn)
                    for msisdn in self.store.set_members(self.members_key)]

    def is_member(self, user_record):
        return user_record in self.members()

    def remove_member(self, user_record):
        self.store.remove_from_set(self.members_key, user_record['msisdn'])


class GroupStore(RedisStore):

    record_class = GroupStoreRecord

    def generate_key(self, *args):
        return ':'.join(['group'] + map(str, args))

