import redis


def redis_key_maker(key):
    def generate_key(*args):
        return ':'.join([key] + map(str, args))
    return generate_key

user_key = redis_key_maker('user')

class RedisStore(object):

    def __init__(self, redis_class = redis.Redis):
        self.server = redis_class()

    def authenticate(self, username, password):
        user = self.server.hgetall(user_key(username))
        return user and user.get('password') == password

    def register(self, username, password):
        return self.server.hset(user_key(username), 'password', password)

    def user_exists(self, username):
        return self.server.exists(user_key(username))

