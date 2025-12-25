from tod import TodStatements
import discord

statements = TodStatements()

# ---------------- JOIN GAME BUTTONS ----------------
class GameControlView(discord.ui.View):
    def __init__(self, guild_id: int, games: dict):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.games = games

    @discord.ui.button(
        style=discord.ButtonStyle.success,
        emoji="➕"
    )
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        gid = self.guild_id
        game = self.games.get(gid)

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

        embed = discord.Embed(
            title="✅ Player Joined!",
            description=f"**{interaction.user.mention}** joined the game!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Total Players",
            value=f"👥 {len(game['players'])}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(
        style=discord.ButtonStyle.danger,
        emoji="➖"
    )
    async def quit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        gid = self.guild_id
        game = self.games.get(gid)

        if not game:
            return await interaction.response.send_message(
                "❌ No active game.",
                ephemeral=True
            )

        user_id = interaction.user.id

        # Overseer quits → end game
        if user_id == game["overseer"]:
            player_count = len(game["players"])
            del self.games[gid]
            
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

        if user_id not in game["players"]:
            return await interaction.response.send_message(
                "❌ You are not in the game.",
                ephemeral=True
            )

        game["players"].remove(user_id)

        if game["current"] == user_id:
            game["current"] = None

        embed = discord.Embed(
            title="🚪 Player Left",
            description=f"**{interaction.user.mention}** has quit the game.",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="Players Remaining",
            value=f"👥 {len(game['players'])}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

# ---------------- SELECT T/D BUTTONS ----------------
class GameTurnView(discord.ui.View):
    def __init__(self, guild_id: int, games: dict):
        super().__init__(timeout=None)
        self.guild_id = guild_id
        self.games = games

    # -------- TRUTH --------
    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="❔", label="Truth")
    async def truth_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        gid = self.guild_id
        game = self.games.get(gid)

        if not game or game["current"] is None:
            return await interaction.response.send_message("❌ No active turn.", ephemeral=True)

        if interaction.user.id != game["current"]:
            return await interaction.response.send_message("❌ Not your turn.", ephemeral=True)

        question = statements.get_truth()
        game["current"] = None

        embed = discord.Embed(
            title="🧠 Truth Time!",
            description=question,
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Player",
            value=interaction.user.mention,
            inline=False
        )
        
        embed.set_footer(text="Overseer can use /pick for the next player!")

        await interaction.response.send_message(embed=embed)

    # -------- DARE --------
    @discord.ui.button(style=discord.ButtonStyle.primary, emoji="❗", label="Dare")
    async def dare_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        gid = self.guild_id
        game = self.games.get(gid)

        if not game or game["current"] is None:
            return await interaction.response.send_message("❌ No active turn.", ephemeral=True)

        if interaction.user.id != game["current"]:
            return await interaction.response.send_message("❌ Not your turn.", ephemeral=True)

        challenge = statements.get_dare()
        game["current"] = None

        embed = discord.Embed(
            title="🔥 Dare Challenge!",
            description=challenge,
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="Player",
            value=interaction.user.mention,
            inline=False
        )
        
        embed.set_footer(text="Overseer can use /pick for the next player!")

        await interaction.response.send_message(embed=embed)
    
    # -------- JOIN --------
    @discord.ui.button(
        style=discord.ButtonStyle.success,
        emoji="➕"
    )
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        gid = self.guild_id
        game = self.games.get(gid)

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

        embed = discord.Embed(
            title="✅ Player Joined!",
            description=f"**{interaction.user.mention}** joined the game!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="Total Players",
            value=f"👥 {len(game['players'])}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    # -------- QUIT --------
    @discord.ui.button(
        style=discord.ButtonStyle.danger,
        emoji="➖"
    )
    async def quit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        gid = self.guild_id
        game = self.games.get(gid)

        if not game:
            return await interaction.response.send_message(
                "❌ No active game.",
                ephemeral=True
            )

        user_id = interaction.user.id

        # Overseer quits → end game
        if user_id == game["overseer"]:
            player_count = len(game["players"])
            del self.games[gid]
            
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

        if user_id not in game["players"]:
            return await interaction.response.send_message(
                "❌ You are not in the game.",
                ephemeral=True
            )

        game["players"].remove(user_id)

        if game["current"] == user_id:
            game["current"] = None

        embed = discord.Embed(
            title="🚪 Player Left",
            description=f"**{interaction.user.mention}** has quit the game.",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="Players Remaining",
            value=f"👥 {len(game['players'])}",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)