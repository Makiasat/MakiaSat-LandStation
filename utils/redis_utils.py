from typing import Awaitable, Union

from redis import Redis
from pickle import dumps, loads


class RedisClient:
    def __init__(self, key: str, host: str = 'localhost', port: int = 6379) -> None:
        self.key: str = key
        self.host: str = host
        self.port: int = port

        self.client: Redis = Redis(host=self.host, port=self.port)

    def initial_del(self) -> None:
        self.client.delete(self.key)

    def push_list(self, element: list) -> Union[Awaitable[int], int]:
        return self.client.lpush(self.key, dumps(element))

    def pop_list(self) -> None or list:
        res = self.client.rpop(self.key)
        if type(res) in (bytes, bytearray):
            return loads(res)
        else:
            return None

