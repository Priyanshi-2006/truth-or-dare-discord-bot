# Truth or Dare Discord Bot

A fully interactive **Truth or Dare Discord bot** built using **discord.py**.
The bot supports slash commands, button-based interactions, and structured game flow with an overseer and multiple players.

---

## Features

* Slash command based interaction (`/start_game`, `/join`, etc.)
* Button-driven UI using Discord Views
* Overseer-controlled game flow
* Player join and leave system
* Automatic random turn selection
* Separate Truth and Dare handling
* Clean modular code structure
* Persistent game state per guild

---

## How the Bot Works

1. A user starts a game using a slash command.
2. That user becomes the **Overseer**.
3. Other users join the game using buttons.
4. The overseer controls when the game starts.
5. Each round randomly selects a player.
6. The player chooses **Truth** or **Dare** via buttons.
7. The bot sends the corresponding prompt.

All game state is stored **in-memory per guild**, allowing multiple servers to run games independently.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/areeb-x3/truth-or-dare-discord-bot.git
cd truth-or-dare-discord-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Bot

Create a `config.py` file:

```python
API_KEY = "YOUR_DISCORD_BOT_TOKEN"
```

---

## Running the Bot

```bash
python main.py
```

---

## Commands

| Command       | Description                     |
| ------------- | ------------------------------- |
| `/start_game` | Starts a new Truth or Dare game |
| `/end_game`   | Ends the active game            |
| `/pick`       | Pick a random player            |

---

## Permissions Required

* Send Messages
* Use Application Commands
* Embed Links
* Read Message History

---

## Notes

* Overseer cannot join as a player.
* Duplicate joins are prevented.

