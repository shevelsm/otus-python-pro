import redis


class RedisAsStorage:
    def __init__(
            self,
            host: str='localhost',
            port: int=6379,
            db: int=0,
            timeout: int=3,
            connect_now: bool=True
        ) -> None:
            self.host = host
            self.port = port
            self.db = db
            self.timeout = timeout

            if connect_now is True:
                  self.connect()

    def connect(self):
        self.con = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            socket_connect_timeout=self.timeout,
            socket_timeout=self.timeout
        )
    
    def get(self, key):
        try:
            value = self.con.get(key)
            return value.decode() if value else value
        except:
               raise ConnectionError
    
    def set(self, key, value, ttl):
        try:
            return self.con.set(key, value, ex=ttl)
        except:
             raise ConnectionError
        