import asyncio
import asyncpg
from os import path
from aiosqlite import connect
from apscheduler.triggers.cron import CronTrigger


class Database:

    # dsn = None
    # pool = None

    def __init__(self, bot, dsn):
        self.bot = bot
        self.build_path = f"{self.bot._static}/build.sql"
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.init_instance(dsn))

    async def init_instance(self, dsn):
        self.pool = await asyncpg.create_pool(dsn)        

    #TODO Follow up on whether a singleton is required
    # @classmethod()
    # def set_dsn(cls, dsn):
    #     #Database.dsn = dsn
    #     cls.dsn = dsn

    # @classmethod()
    # async def _pool(cls):
    #     if not isinstance(cls.dsn, str):
    #         raise TypeError("dsn must be a string")        
    #     if cls.pool is None:
    #         cls.pool = await asyncpg.create_pool(Database.dsn)
    #     return cls.pool

    async def field(self, sql, *values):
        with self.pool.acquire() as conn:
            return await conn.fetchval(sql, *values)
        
    async def record(self, sql, *values):
        with self.pool.acquire() as conn:
            return await conn.fetchrow(sql, *values)

    async def records(self, sql, *values):
        with self.pool.acquire() as conn:
            return await conn.fetch(sql, *values)

    async def column(self, sql, *values):
        with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *values)
            return [row[0] for row in rows]

    async def execute(self, sql, *values):
        self._calls += 1

    async def executemany(self, sql, valueset):
        self._calls += 1

    async def executescript(self, path, *values):
        self._calls += 1
