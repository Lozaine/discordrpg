# One Piece RPG Discord Bot

An advanced Discord bot for roleplaying in the world of One Piece! Create characters, form crews, embark on quests, engage in combat, and shape your destiny across the seas.

## Features

- **Character Creation & Management**: Create and customize your own pirate, marine, or adventurer.
- **Crew System**: Form or join crews, assign roles, and manage your pirate band.
- **Ship Management**: Build, upgrade, and manage ships for your crew.
- **Quest System**: Take on story-driven quests inspired by the East Blue Saga and beyond.
- **Combat System**: Engage in PvP and PvE battles with unique mechanics.
- **Ally Recruitment**: Recruit allies to aid your journey.
- **Faction Reputation**: Build your standing with various One Piece world factions.
- **Persistent Data**: All progress is saved and managed automatically.

## Getting Started

### Prerequisites
- Python 3.11+
- A Discord bot token ([How to create a bot](https://discordpy.readthedocs.io/en/stable/discord.html))

### Installation
1. Clone the repository:
	```bash
	git clone https://github.com/Elenyx/onepiecerpg-bot.git
	cd onepiecerpg-bot
	```
2. Install dependencies:
	```bash
	pip install -r requirements.txt
	# or, if using pyproject.toml:
	pip install .
	```
3. Set your Discord bot token as an environment variable:
	```bash
	export DISCORD_BOT_TOKEN=your_token_here
	```
4. Run the bot:
	```bash
	python main.py
	```

## Usage

Once the bot is running and invited to your server, use the following commands (with the default prefix `!`):

### Character Commands
- `/create_character` — Create a new character
- `/character_profile` — View your character's profile
- `/delete_character` — Delete a character

### Crew Commands
- `/create_crew` — Create a new crew
- `/join_crew` — Join an existing crew
- `/crew_info` — View crew details

### Ship Commands
- `/ship` — View your crew's ship
- `/upgrade_ship` — Upgrade your ship

### Quest Commands
- `/quests` — View available and active quests
- `/accept_quest` — Accept a quest
- `/complete_quest` — Complete a quest

### Combat Commands
- `/challenge` — Challenge another player to PvP
- `/battle` — Start a PvE battle

### Ally & Reputation
- `/allies` — View and manage allies
- `/reputation` — View your reputation with factions

## Configuration

Edit `config.py` to adjust bot settings, such as command prefix, embed colors, and XP multipliers.

## Data Storage

All persistent data (characters, crews, ships, etc.) is stored in the `data/` directory as JSON files.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

This project is for educational and fan purposes only. Not affiliated with Toei, Shueisha, or Eiichiro Oda.