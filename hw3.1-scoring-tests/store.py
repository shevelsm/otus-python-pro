from redis.backoff import ExponentialBackoff
from redis.retry import Retry
from redis.client import Redis
from redis.exceptions import BusyLoadingError, ConnectionError, TimeoutError


DEFAULT_TTL = 100


class RedisAsStorage:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        timeout: int = 5,
        retries: int = 5,
        connect_now: bool = True,
    ) -> None:
        self.host = host
        self.port = port
        self.db = db
        self.timeout = timeout
        self.retries = retries

        if connect_now is True:
            self.connect()

    def connect(self):
        self.con = Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            retry=Retry(ExponentialBackoff(cap=0.512, base=0.008), self.retries),
            retry_on_error=[BusyLoadingError, ConnectionError, TimeoutError],
            socket_connect_timeout=self.timeout,
            socket_timeout=self.timeout,
        )

    def get(self, key):
        try:
            value = self.con.get(key)
            return value.decode() if value else value
        except:
            raise ConnectionError

    def set(self, key, value, ttl=DEFAULT_TTL):
        try:
            return self.con.set(key, value, ex=ttl)
        except:
            raise ConnectionError
