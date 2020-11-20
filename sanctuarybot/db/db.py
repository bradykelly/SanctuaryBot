import asyncio
import asyncpg
from os import path
from aiosqlite import connect
from apscheduler.triggers.cron import CronTrigger


class Database:

    def __init__(self, bot, dsn):
        self.bot = bot
        self.build_path = f"{self.bot._static}/build.sql"
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.init_instance(dsn))

    async def init_instance(self, dsn):
        self.pool = await asyncpg.create_pool(dsn)  

    async def sync(self):
        # Insert.
        await self.executemany("INSERT INTO guild_config (guild_id) VALUES ($1) ON CONFLICT DO NOTHING", [(g.id,) for g in self.bot.guilds])              

        # Remove.
        stored = await self.column("SELECT guild_id FROM guild_config")
        member_of = [g.id for g in self.bot.guilds]
        removals = [(g_id,) for g_id in set(stored) - set(member_of)]
        await self.executemany("DELETE FROM guild_config WHERE guild_id = $1", removals)        

    async def field(self, sql, *values):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(sql, *values)
        
    async def record(self, sql, *values):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(sql, *values)

    async def records(self, sql, *values):
        async with self.pool.acquire() as conn:
            return await conn.fetch(sql, *values)

    async def column(self, sql, *values):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *values)
            return [row[0] for row in rows]

    async def execute(self, sql, *values):
        async with self.pool.acquire() as conn:
            await conn.execute(sql, *values)

    async def executemany(self, sql, valueset):
        async with self.pool.acquire() as conn:
            await conn.executemany(sql, valueset)

    async def executescript(self, path, *values):
        pass
