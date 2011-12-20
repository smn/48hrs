import redis

class RedisStoreException(Exception): pass
class RecordDoesNotExist(RedisStoreException): pass

class RedisRecord(object):

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

    def reload(self):
        return self.store.record(self.key, self.store.read_dict(self.key))

class RedisStore(object):

    record_class = RedisRecord

    def __init__(self, redis_class=redis.Redis):
        self.server = redis_class()

    def generate_key(self, key):
        raise RedisStoreException('Please override the generate_key() function')

    def key_exists(self, key):
        return self.server.exists(key)

    def record(self, key, data):
        return self.record_class(self, key, **data)

    def save_dict(self, key, data):
        self.server.hmset(key, data)

    def read_dict(self, key):
        return self.server.hgetall(key)

    def create(self, pk, data):
        key = self.generate_key(pk)
        record = self.record(key, data)
        record.save()
        return record

    def find(self, pk):
        key = self.generate_key(pk)
        if self.key_exists(key):
            data = self.read_dict(key)
            return self.record(key, data)
        raise RecordDoesNotExist('Cannot find record with key %s' % (repr(key),))


class UserStore(RedisStore):

    def generate_key(self, msisdn):
        return 'user:%s' % (msisdn,)

    def authenticate(self, username, password):
        user = self.read_dict(self.generate_key(username))
        return user and user.get('password') == password

    def register(self, username, password):
        return self.create(username, {'password': password})

    def user_exists(self, username):
        return self.key_exists(self.generate_key(username))


class GroupStore(RedisStore):

    def generate_key(self, name):
        return 'group:%s' % (name,)
