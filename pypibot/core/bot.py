import hikari
import lightbulb
import os

from pathlib import Path
from .database import Database
from .config import Config
from hikari import events
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class Bot(lightbulb.Bot):
    def __init__(self, version: str) -> None:
        self.prefix = self.get_custom_prefix
        self.scheduler = AsyncIOScheduler()
        self.version = version
        self._plugins = [p.stem for p in Path(".").glob("./pypibot/core/plugins/*.py")]
        
        self.config = Config()
        self.db = Database()

        super().__init__(
            prefix=self.prefix, 
            token=self.config.token,
            insensitive_commands=True, 
            owner_ids=self.config.owner_id
        )

        subscriptions = {
            events.StartingEvent: self.on_starting,
            events.StartedEvent: self.on_started,
            events.StoppingEvent: self.on_stopping,
            events.GuildAvailableEvent: self.on_guild_join,
            events.GuildLeaveEvent: self.on_guild_leave,
        }
        for e, c in subscriptions.items():
            self._event_manager.subscribe(e, c)
    
    # Gets guild prefix from all the guilds
    def get_custom_prefix(self, bot, message):
        prefix = self.db.field("SELECT Prefix FROM Guilds WHERE GuildID = ?", message.guild.id)
        return lightbulb.when_mentioned_or(prefix)(bot, message)
    
    # Event when the bot is starting
    async def on_starting(self, event: events.StartingEvent):
        self.db.connect()

        for plugin in self._plugins:
            try:
                self.load_extension(f"pypibot.core.plugins.{plugin}")
                print(f"Loaded {plugin}")

            except lightbulb.errors.ExtensionMissingLoad:
                print(f"Plugin {plugin} is missing the load function")

        
    # Event once the bot started
    async def on_started(self, event: events.StartedEvent):
        self.scheduler.start()

    async def on_stopping(self, event: events.StoppingEvent):
        self.scheduler.shutdown()
        self.db.close()

    async def on_guild_join(self, event: events.GuildAvailableEvent):
        await self.db.execute("INSERT INTO GUILDS (GuildID) VALUES (?)", event.guild.id)

    async def on_guild_leave(self, event: events.GuildLeaveEvent):
        await self.db.execute("DELETE FROM Guilds WHERE GuildID = ?", event.guild_id)
