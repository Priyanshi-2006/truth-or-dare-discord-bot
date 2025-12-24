import config
import discord
from discord import app_commands

TOKEN = config.API_KEY

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

client = MyClient()

@client.tree.command(name="echo", description="Replies with Hello world")
async def echo(interaction: discord.Interaction):
    await interaction.response.send_message("Hello world")

client.run(TOKEN)
