import config
import discord
import random
from discord import app_commands

TOKEN = config.API_KEY

TRUTHS = [
    "What's your biggest fear?",
    "Who was your first crush?",
    "What's a secret no one knows?",
    "Have you ever lied to your best friend?",
    "What's the most embarrassing thing you've done?",
    "Who do you have a crush on right now?",
    "What's your guilty pleasure?",
    "Have you ever cheated on a test?"
]

DARES = [
    "Send your last used emoji 10 times",
    "Change your nickname to something embarrassing for 5 minutes",
    "Say 'I love this server' in all caps 3 times",
    "Do 10 pushups and post proof",
    "Send a voice message singing your favorite song",
    "Change your profile picture to something funny",
    "Compliment every person online right now"
]

games = {}

# ---------------- JOIN/LEAVE GAME BUTTONS ----------------
class GameControlView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(
        style=discord.ButtonStyle.success,
        emoji="➕"
    )
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        gid = self.guild_id
        game = games.get(gid)

        if not game:
            return await interaction.response.send_message(
                "❌ No active game.",
                ephemeral=True
            )

        if interaction.user.id == game["overseer"]:
            return await interaction.response.send_message(
                "❌ Overseer cannot join as a player.",
                ephemeral=True
            )

        if interaction.user.id in game["players"]:
            return await interaction.response.send_message(
                "⚠️ You already joined the game.",
                ephemeral=True
            )

        game["players"].add(interaction.user.id)

        await interaction.response.send_message(
            f"✅ You joined the game!\n"
            f"👥 Players: {len(game['players'])}",
            ephemeral=True
        )

    @discord.ui.button(
        style=discord.ButtonStyle.danger,
        emoji="➖"
    )
    async def quit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        gid = self.guild_id
        game = games.get(gid)

        if not game:
            return await interaction.response.send_message(
                "❌ No active game.",
                ephemeral=True
            )

        user_id = interaction.user.id

        # Overseer quits → end game
        if user_id == game["overseer"]:
            del games[gid]
            return await interaction.response.send_message(
                "🛑 Overseer quit. Game ended.",
                ephemeral=True
            )

        if user_id not in game["players"]:
            return await interaction.response.send_message(
                "❌ You are not in the game.",
                ephemeral=True
            )

        game["players"].remove(user_id)

        if game["current"] == user_id:
            game["current"] = None

        await interaction.response.send_message(
            f"🚪 You quit the game.\n"
            f"👥 Players remaining: {len(game['players'])}",
            ephemeral=True
        )

class GameTurnView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    # -------- TRUTH --------
    @discord.ui.button(style=discord.ButtonStyle.primary, label="Truth")
    async def truth_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        gid = self.guild_id
        game = games.get(gid)

        if not game or game["current"] is None:
            return await interaction.response.send_message("❌ No active turn.", ephemeral=True)

        if interaction.user.id != game["current"]:
            return await interaction.response.send_message("❌ Not your turn.", ephemeral=True)

        question = random.choice(TRUTHS)
        game["current"] = None

        await interaction.response.send_message(
            f"🧠 **Truth:**\n>>> {question}",
            ephemeral=False
        )

    # -------- DARE --------
    @discord.ui.button(style=discord.ButtonStyle.secondary, label="Dare")
    async def dare_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        gid = self.guild_id
        game = games.get(gid)

        if not game or game["current"] is None:
            return await interaction.response.send_message("❌ No active turn.", ephemeral=True)

        if interaction.user.id != game["current"]:
            return await interaction.response.send_message("❌ Not your turn.", ephemeral=True)

        challenge = random.choice(DARES)
        game["current"] = None

        await interaction.response.send_message(
            f"🔥 **Dare:**\n>>> {challenge}",
            ephemeral=False
        )
    
class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  # Enable message content intent
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
    
    async def setup_hook(self):
        # Sync commands globally
        await self.tree.sync()
        print("Commands synced!")

client = MyClient()

@client.event
async def on_ready():
    print(f'Logged in as {client.user}!')
    print(f'Bot is in {len(client.guilds)} guilds')

# ---------------- START GAME ----------------
@client.tree.command(name="start_game", description="Start a truth or dare game")
async def start_game(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message(
            "❌ This command only works in servers.",
            ephemeral=True
        )

    gid = interaction.guild.id

    if gid in games:
        overseer = interaction.guild.get_member(games[gid]["overseer"])
        return await interaction.response.send_message(
            f"❌ A game is already running.\n"
            f"👑 Overseer: **{overseer.name if overseer else 'Unknown'}**",
            ephemeral=True
        )

    games[gid] = {
        "overseer": interaction.user.id,
        "players": set(),
        "current": None
    }

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

    view = GameControlView(guild_id=gid)

    await interaction.response.send_message(
        embed=embed,
        view=view
    )

# ---------------- JOIN GAME ----------------
@client.tree.command(name="join_game", description="Join the truth or dare game")
async def join_game(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command only works in servers.", ephemeral=True)
    
    gid = interaction.guild.id
    if gid not in games:
        return await interaction.response.send_message("❌ No active game. Use `/start_game` first!", ephemeral=True)
    
    game = games.get(gid)
    # BLOCK OVERSEER FROM JOINING
    if interaction.user.id == game["overseer"]:
        return await interaction.response.send_message(
            "❌ The overseer cannot join the game as a player.",
            ephemeral=True
        )

    # OPTIONAL: prevent duplicate joins
    if interaction.user.id in game["players"]:
        return await interaction.response.send_message(
            "⚠️ You have already joined the game.",
            ephemeral=True
        )
    
    games[gid]["players"].add(interaction.user.id)
    player_count = len(games[gid]["players"])
    await interaction.response.send_message(
        f"✅ **{interaction.user.name}** joined the game!\n"
        f"👥 Players: {player_count}"
    )

# ---------------- QUIT GAME ------------------
@client.tree.command(name="quit_game", description="Quit the current truth or dare game")
async def quit_game(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message(
            "❌ This command only works in servers.",
            ephemeral=True
        )

    gid = interaction.guild.id
    game = games.get(gid)

    if not game:
        return await interaction.response.send_message(
            "❌ No active game to quit.",
            ephemeral=True
        )

    user_id = interaction.user.id

    if user_id == game["overseer"]:
        player_count = len(game["players"])
        del games[gid]
        return await interaction.response.send_message(
            f"🛑 **Overseer has quit the game.**\n"
            f"🎮 Game ended. Total players were: {player_count}"
        )

    if user_id not in game["players"]:
        return await interaction.response.send_message(
            "❌ You are not part of the current game.",
            ephemeral=True
        )

    game["players"].remove(user_id)


    if game["current"] == user_id:
        game["current"] = None

    await interaction.response.send_message(
        f"🚪 **{interaction.user.name}** has quit the game.\n"
        f"👥 Players remaining: {len(game['players'])}"
    )

# ---------------- PICK PLAYER ----------------
@client.tree.command(name="pick", description="Pick a random player (overseer only)")
async def pick(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command only works in servers.", ephemeral=True)
    
    gid = interaction.guild.id
    game = games.get(gid)
    
    if not game:
        return await interaction.response.send_message("❌ No active game.", ephemeral=True)
    
    if interaction.user.id != game["overseer"]:
        return await interaction.response.send_message("❌ Only the overseer can pick players.", ephemeral=True)
    
    if not game["players"]:
        return await interaction.response.send_message("❌ No players have joined yet!")
    
    chosen = random.choice(list(game["players"]))
    game["current"] = chosen
    user = await interaction.guild.fetch_member(chosen)
    
    embed = discord.Embed(
        title="🎯 Player Selected",
        description=f"**{user.mention}** has been chosen!",
        color=discord.Color.gold()
    )

    embed.add_field(
        name="Next Step",
        value="Choose `/truth` or `/dare`",
        inline=False
    )

    embed.set_footer(text="Players can still join or quit below")

    view = GameTurnView(guild_id=gid)

    await interaction.response.send_message(
        embed=embed,
        view=view
    )

# ---------------- TRUTH ----------------
@client.tree.command(name="truth", description="Choose truth")
async def truth(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command only works in servers.", ephemeral=True)
    
    gid = interaction.guild.id
    game = games.get(gid)
    
    if not game:
        return await interaction.response.send_message("❌ No active game.", ephemeral=True)
    
    if game["current"] is None:
        return await interaction.response.send_message("❌ No one has been picked yet!", ephemeral=True)
    
    if interaction.user.id != game["current"]:
        return await interaction.response.send_message("❌ It's not your turn!", ephemeral=True)
    
    selected_truth = random.choice(TRUTHS)
    game["current"] = None  # Reset current player
    
    await interaction.response.send_message(
        f"🧠 **Truth for {interaction.user.mention}:**\n"
        f">>> {selected_truth}\n\n"
        f"Overseer can use `/pick` for the next player!"
    )

# ---------------- DARE ----------------
@client.tree.command(name="dare", description="Choose dare")
async def dare(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command only works in servers.", ephemeral=True)
    
    gid = interaction.guild.id
    game = games.get(gid)
    
    if not game:
        return await interaction.response.send_message("❌ No active game.", ephemeral=True)
    
    if game["current"] is None:
        return await interaction.response.send_message("❌ No one has been picked yet!", ephemeral=True)
    
    if interaction.user.id != game["current"]:
        return await interaction.response.send_message("❌ It's not your turn!", ephemeral=True)
    
    selected_dare = random.choice(DARES)
    game["current"] = None  # Reset current player
    
    await interaction.response.send_message(
        f"🔥 **Dare for {interaction.user.mention}:**\n"
        f">>> {selected_dare}\n\n"
        f"Overseer can use `/pick` for the next player!"
    )

# ---------------- END GAME ----------------
@client.tree.command(name="end_game", description="End the current game (overseer only)")
async def end_game(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command only works in servers.", ephemeral=True)
    
    gid = interaction.guild.id
    game = games.get(gid)
    
    if not game:
        return await interaction.response.send_message("❌ No active game.", ephemeral=True)
    
    if interaction.user.id != game["overseer"]:
        return await interaction.response.send_message("❌ Only the overseer can end the game.", ephemeral=True)
    
    player_count = len(game["players"])
    del games[gid]
    
    await interaction.response.send_message(
        f"🎮 **Game Ended!**\n"
        f"Thanks for playing! Total players: {player_count}"
    )

# ---------------- VIEW PLAYERS ----------------
@client.tree.command(name="players", description="View all players in the current game")
async def players(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message("❌ This command only works in servers.", ephemeral=True)
    
    gid = interaction.guild.id
    game = games.get(gid)
    
    if not game:
        return await interaction.response.send_message("❌ No active game.", ephemeral=True)
    
    if not game["players"]:
        return await interaction.response.send_message("❌ No players have joined yet!")
    
    player_list = []
    for player_id in game["players"]:
        member = interaction.guild.get_member(player_id)
        if member:
            player_list.append(member.name)
    
    overseer = interaction.guild.get_member(game["overseer"])
    
    await interaction.response.send_message(
        f"👥 **Current Players ({len(player_list)}):**\n"
        f"{', '.join(player_list)}\n\n"
        f"👑 **Overseer:** {overseer.name if overseer else 'Unknown'}"
    )

# ---------------- DEBUG COMMANDS ----------------
@client.tree.command(name="debug", description="Debug")
async def debug(interaction: discord.Interaction):
    await interaction.response.send_message(f"{games}")

@client.tree.command(name="embed", description="Sends a sample embed")
async def embed(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Hello from an Embed",
        description="This is a Discord embed message.",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="Field 1",
        value="Some text here",
        inline=False
    )

    embed.set_footer(text="Embed footer")

    await interaction.response.send_message(embed=embed)

client.run(TOKEN)