# Built-in Modules
import json, random

# -----------------------------------------------------------------------
# TRUTH AND DARE GAME LOGIC:
# This is the actual game logic (backend) 
# that is used by the discord bot.
# -----------------------------------------------------------------------

class TodGame:
    def __init__(self):
        self.games = {}
    
    # Start a new game for a guild    
    def start_game(self, gid, overseer_id):
        if gid in self.games:
            return False, "A game is already running."
        
        self.games[gid] = {
            "overseer": overseer_id,
            "players": set(),
            "current": None
        }
        return True, "Game started successfully."
    
    # End the game for a guild
    def end_game(self, gid):
        if gid not in self.games:
            return False, "No active game.", 0
        
        player_count = len(self.games[gid]["players"])
        del self.games[gid]
        return True, "Game ended.", player_count
    
    # Check if a game exists for a guild
    def game_exists(self, gid):
        return gid in self.games
    
    # Get game data for a guild
    def get_game(self, gid):
        return self.games.get(gid)
    
    # Check if user is the overseer
    def is_overseer(self, gid, user_id):
        game = self.games.get(gid)
        if not game:
            return False
        return game["overseer"] == user_id
    
    # Add a player to the game
    def join_game(self, gid, user_id):
        game = self.games.get(gid)
        if not game:
            return False, "No active game."
        
        if user_id == game["overseer"]:
            return False, "The overseer cannot join as a player."
        
        if user_id in game["players"]:
            return False, "Already joined."
        
        game["players"].add(user_id)
        return True, f"Joined successfully. Total players: {len(game['players'])}"
    
    # Remove a player from the game
    def quit_game(self, gid, user_id):
        game = self.games.get(gid)
        if not game:
            return False, "No active game.", 0, False
        
        # If overseer quits, end the game
        if user_id == game["overseer"]:
            player_count = len(game["players"])
            del self.games[gid]
            return True, "Overseer quit. Game ended.", player_count, True
        
        if user_id not in game["players"]:
            return False, "Not part of the game.", 0, False
        
        game["players"].remove(user_id)
        
        # Reset current player if they quit
        if game["current"] == user_id:
            game["current"] = None
        
        return True, "Quit successfully.", len(game["players"]), False
    
    # Pick a random player for the turn
    def pick_player(self, gid):
        game = self.games.get(gid)
        if not game:
            return False, "No active game.", None
        
        if not game["players"]:
            return False, "No players have joined yet.", None
        
        chosen = random.choice(list(game["players"]))
        game["current"] = chosen
        return True, "Player picked.", chosen
    
    # Get the current player's turn
    def get_current_player(self, gid):
        game = self.games.get(gid)
        if not game:
            return None
        return game.get("current")
    
    # Check if it's the user's turn
    def is_current_player(self, gid, user_id):
        game = self.games.get(gid)
        if not game:
            return False
        return game.get("current") == user_id
    
    # Reset the current player after their turn
    def reset_current_player(self, gid):
        game = self.games.get(gid)
        if game:
            game["current"] = None
    
    # Get list of player IDs
    def get_players(self, gid):
        game = self.games.get(gid)
        if not game:
            return []
        return list(game["players"])
    
    # Get the overseer's ID
    def get_overseer(self, gid):
        game = self.games.get(gid)
        if not game:
            return None
        return game["overseer"]

# -----------------------------------------------------------------------
# TRUTH AND DARE STATEMENTS:
# Used to fetch and randomly choose dares,
# Statements are fetched from statements.json.
# -----------------------------------------------------------------------

class TodStatements:
    # Fecthes Statements
    def __init__(self):
        with open("statements.json", "r") as file:
            data = json.load(file)
        
        self.TRUTHS = data["TRUTHS"]
        self.DARES = data["DARES"]
    
    # Grabbing a dare
    def get_dare(self):
        if len(self.DARES) == 0:
            self.refetch_statements("DARE")
        return self.DARES.pop(random.randrange(len(self.DARES)))
    
    # Grabbing a truth
    def get_truth(self):
        if len(self.TRUTHS) == 0:
            self.refetch_statements("TRUTH")
        return self.TRUTHS.pop(random.randrange(len(self.TRUTHS)))
    
    # Refetching Statements in case they exhaust
    def refetch_statements(self, type):
        with open("statements.json", "r") as file:
            data = json.load(file)
        
        if type == "DARE":
            self.DARES = data["DARES"]
        elif type == "TRUTH":
            self.TRUTHS = data["TRUTHS"]

    def debug(self):
        print(self.TRUTHS, self.DARES)