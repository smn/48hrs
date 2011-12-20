import redis

class RedisStore(object):
    
    def __init__(self, redis_class = redis.Redis):
        self.server = redis_class()
    
    def authenticate(self, username, password):        
        user = self.server.hgetall('user:%s' % username)        
        return user and user.get('password') == password
    
    def register(self, username, password):
        return self.server.hset('user:%s' % username, 'password', password)
    
    def user_exists(self, username):
        return self.server.exists('user:%s' % username)
    