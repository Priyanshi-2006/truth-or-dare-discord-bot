# Local Modules
import config
from views import GameControlView, GameTurnView
from tod import TodGame, TodStatements

# Built-in/Installed Modules
import discord
from discord import app_commands

# -----------------------------------------------------------------------
# MAIN ENGINE OF THE DISCORD BOT
# -----------------------------------------------------------------------
class TodBotClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # Enable message content intent
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        # Sync commands globally
        await self.tree.sync()
        print("Commands synced!")

# Initialising
client = TodBotClient()
tod = TodGame()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')
    print(f'Bot is in {len(client.guilds)} guilds')

# -----------------------------------------------------------------------
# BOT COMMANDS
# -----------------------------------------------------------------------

# START GAME
@client.tree.command(name="start_game", description="Start a truth or dare game")
async def start_game(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message(
            "❌ This command only works in servers.",
            ephemeral=True
        )

    gid = interaction.guild.id
    success, message = tod.start_game(gid, interaction.user.id)
    
    if not success:
        overseer = interaction.guild.get_member(tod.get_overseer(gid))
        return await interaction.response.send_message(
            f"❌ {message}\n"
            f"👑 Overseer: **{overseer.name if overseer else 'Unknown'}**",
            ephemeral=True
        )

    embed = discord.Embed(
        title="🎮 Truth or Dare Game Started!",
        description="Use the buttons below to join or quit.",
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="Overseer",
        value=interaction.user.mention,
        inline=False
    )

    view = GameControlView(guild_id=gid, games=tod.games)

    await interaction.response.send_message(
        embed=embed,
        view=view
    )

# JOIN GAME
@client.tree.command(name="join_game", description="Join the truth or dare game")
async def join_game(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command only works in servers.", ephemeral=True)
    
    gid = interaction.guild.id
    success, message = tod.join_game(gid, interaction.user.id)
    
    if not success:
        return await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    embed = discord.Embed(
        title="✅ Player Joined!",
        description=f"**{interaction.user.mention}** joined the game!",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="Total Players",
        value=f"👥 {message.split(': ')[1]}",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

# QUIT GAME
@client.tree.command(name="quit_game", description="Quit the current truth or dare game")
async def quit_game(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message(
            "❌ This command only works in servers.",
            ephemeral=True
        )

    gid = interaction.guild.id
    success, message, player_count, overseer_quit = tod.quit_game(gid, interaction.user.id)
    
    if not success:
        return await interaction.response.send_message(
            f"❌ {message}",
            ephemeral=True
        )
    
    if overseer_quit:
        embed = discord.Embed(
            title="🛑 Game Ended",
            description="**Overseer has quit the game.**",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Total Players",
            value=f"👥 {player_count}",
            inline=False
        )
        return await interaction.response.send_message(embed=embed)
    
    embed = discord.Embed(
        title="🚪 Player Left",
        description=f"**{interaction.user.mention}** has quit the game.",
        color=discord.Color.orange()
    )
    
    embed.add_field(
        name="Players Remaining",
        value=f"👥 {player_count}",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

# PICK PLAYER
@client.tree.command(name="pick", description="Pick a random player (overseer only)")
async def pick(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command only works in servers.", ephemeral=True)
    
    gid = interaction.guild.id
    
    if not tod.game_exists(gid):
        return await interaction.response.send_message("❌ No active game.", ephemeral=True)
    
    if not tod.is_overseer(gid, interaction.user.id):
        return await interaction.response.send_message("❌ Only the overseer can pick players.", ephemeral=True)
    
    success, message, chosen = tod.pick_player(gid)
    
    if not success:
        return await interaction.response.send_message(f"❌ {message}", ephemeral=True)
    
    user = await interaction.guild.fetch_member(chosen)
    
    embed = discord.Embed(
        title="🎯 Player Selected",
        description=f"**{user.mention}** has been chosen!",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="Next Step",
        value="Choose Truth or Dare using the buttons below",
        inline=False
    )

    embed.set_footer(text="Players can still join or quit below")

    view = GameTurnView(guild_id=gid, games=tod.games)

    await interaction.response.send_message(
        embed=embed,
        view=view
    )

# END GAME 
@client.tree.command(name="end_game", description="End the current game (overseer only)")
async def end_game(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command only works in servers.", ephemeral=True)
    
    gid = interaction.guild.id
    
    if not tod.game_exists(gid):
        return await interaction.response.send_message("❌ No active game.", ephemeral=True)
    
    if not tod.is_overseer(gid, interaction.user.id):
        return await interaction.response.send_message("❌ Only the overseer can end the game.", ephemeral=True)
    
    success, message, player_count = tod.end_game(gid)
    
    await interaction.response.send_message(
        f"🎮 **Game Ended!**\n"
        f"Thanks for playing! Total players: {player_count}"
    )

# VIEW PLAYERS
@client.tree.command(name="players", description="View all players in the current game")
async def players(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command only works in servers.", ephemeral=True)
    
    gid = interaction.guild.id
    
    if not tod.game_exists(gid):
        return await interaction.response.send_message("❌ No active game.", ephemeral=True)
    
    player_ids = tod.get_players(gid)
    
    if not player_ids:
        return await interaction.response.send_message("❌ No players have joined yet!")
    
    player_list = []
    for player_id in player_ids:
        member = interaction.guild.get_member(player_id)
        if member:
            player_list.append(member.name)
    
    overseer_id = tod.get_overseer(gid)
    overseer = interaction.guild.get_member(overseer_id)
    
    await interaction.response.send_message(
        f"👥 **Current Players ({len(player_list)}):**\n"
        f"{', '.join(player_list)}\n\n"
        f"👑 **Overseer:** {overseer.name if overseer else 'Unknown'}"
    )

# DEBUG COMMAND: SHOWS GAME DICTIONARY
@client.tree.command(name="debug", description="Debug")
async def debug(interaction: discord.Interaction):
    await interaction.response.send_message(f"{tod.games}")

# -----------------------------------------------------------------------
# RUNNING THE BOT
# -----------------------------------------------------------------------
client.run(config.API_KEY)