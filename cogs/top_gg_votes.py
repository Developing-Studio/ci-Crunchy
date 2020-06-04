import dbl
import json
import time

from datetime import timedelta
from discord.ext import commands, tasks
from colorama import Fore

from logger import Logger

with open("config.json") as file:
    config = json.load(file)


class TopGG(commands.Cog):
    """Handles interactions with the top.gg API"""

    def __init__(self, bot):
        self.bot = bot
        self.token = config.get('dbl_token')
        self.dblpy = dbl.DBLClient(self.bot, self.token,
                                   webhook_path='/dblwebhook',
                                   webhook_auth=config.get("dbl_password"),
                                   webhook_port=config.get("dbl_port"))

    @tasks.loop(minutes=30.0)
    async def update_stats(self):
        """This function runs every 30 minutes to automatically update your server count"""
        try:
            await self.dblpy.post_guild_count()
            Logger.log_dbl('Posted server count ({})'.format(self.dblpy.guild_count()))
        except Exception as e:
            Logger.log_dbl(Fore.RED + 'Failed to post server count\n{}: {}'.format(type(e).__name__, e), error=True)

    @commands.Cog.listener()
    async def on_dbl_vote(self, data):
        now = time.time()
        expires = now + timedelta(hours=24).total_seconds()
        self.bot.database.add_vote(data['user'], expires)
        self.bot.cache.store('votes', data['user'], expires)

    @commands.Cog.listener()
    async def on_dbl_test(self, data):
        now = time.time()
        expires = now + timedelta(hours=24).total_seconds()
        self.bot.database.add_vote(int(data['user']), expires)
        self.bot.cache.store('guilds', int(data['user']),
                             {'_id': int(data['user']), 'expires': expires})


def setup(bot):
    bot.add_cog(TopGG(bot))