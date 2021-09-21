import aiosqlite

from ..config import Config
from apscheduler.triggers.cron import CronTrigger

class Database():
    def __init__(self) -> None:
        self.config = Config()

    async def connect(self):
        self.cxn = await aiosqlite.connect(self.config.data_path)
        await self.executescript(self.config.build_path)
        await self.commit()

    async def commit(self):
        await self.cxn.commit()

    async def close(self):
        await self.cxn.commit()
        await self.cxn.close()

    async def field(self, sql, *values):
        cur = await self.cxn.execute(sql, tuple(values))
        if (row := await cur.fetchone()) is not None:
            return row[0]

    async def record(self, sql, *values):
        cur = await self.cxn.execute(sql, tuple(values))
        return await cur.fetchone()

    async def records(self, sql, *values):
        cur = await self.cxn.execute(sql, tuple(values))
        return await cur.fetchall()

    async def column(self, sql, *values):
        cur = await self.cxn.execute(sql, tuple(values))
        return [row[0] for row in await cur.fetchall()]

    async def execute(self, sql, *values):
        cur = await self.cxn.execute(sql, tuple(values))
        return cur.rowcount

    async def executemany(self, sql, valueset):
        cur = await self.cxn.executemany(sql, valueset)
        return cur.rowcount

    async def executescript(self, path):
        with open(path, "r", encoding="utf-8") as script:
            await self.cxn.executescript(script.read())