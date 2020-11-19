import asyncio
import aiopg
from os import path
from aiosqlite import connect
from apscheduler.triggers.cron import CronTrigger


class Database:

    def __init__(self, bot):
        self.bot = bot
        self.build_path = f"{self.bot._static}/build.sql"
        self._calls = 0

    async def connect(self):
        pass
        #TODO db connection
        self.cxn = await connect(self.db_path)

    async def connect(self):
        pass
        #TODO create conn pool and execute build script


    async def field(self, sql, *values):
        self._calls += 1
        
    async def record(self, sql, *values):
        self._calls += 1

    async def records(self, sql, *values):
        self._calls += 1

    async def column(self, sql, *values):
        self._calls += 1

    async def execute(self, sql, *values):
        self._calls += 1

    async def executemany(self, sql, valueset):
        self._calls += 1

    async def executescript(self, path, *values):
        self._calls += 1
