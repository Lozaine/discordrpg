# Overview

A comprehensive One Piece RPG Discord bot featuring complete character creation, crew management, ship mechanics, PvP/PvE combat systems, quest storylines (East Blue Saga with 6 arcs), ally recruitment, faction alignment, and reputation tracking. The bot provides an immersive RPG experience following the One Piece universe with detailed progression systems, strategic combat, and rich storyline content.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **Discord.py Framework**: Uses discord.ext.commands for command handling and discord interactions for slash commands
- **Cog-based Architecture**: Modular command organization with separate cogs for different bot functionalities
- **Async/Await Pattern**: Full asynchronous operation for handling Discord events and user interactions
- **25 Slash Commands**: Complete command set covering all RPG systems

## Data Management
- **SystemManager Class**: Extended data access layer handling all RPG systems (characters, crews, ships, quests, allies, reputation)
- **JSON File Storage**: Multi-file persistence system for different data types
- **Character Model**: Dataclass-based character representation with stats, inventory, and progression tracking
- **Cross-system Integration**: Seamless data sharing between crews, ships, quests, and reputation systems

## Character System
- **Race-based Bonuses**: 6 races (Human, Fish-Man, Mink, Skypiean, Giant, Cyborg) with unique abilities and stat bonuses
- **Origin-based Storylines**: 6 starting locations determining faction affiliations and initial equipment
- **Dream-based Progression**: 7 character goals unlocking unique skill trees and special commands
- **Multi-character Support**: Users can create up to 3 characters with independent progression
- **Faction Alignment**: Character actions affect standing with Pirates, Marines, Revolutionaries, and World Government

## Crew Management System
- **Crew Creation**: Players can form pirate crews, marine units, or revolutionary cells
- **Role-based Bonuses**: Captain, Navigator, Cook, Doctor, Shipwright, Musician, Fighter roles provide unique benefits
- **Crew Progression**: Crews gain levels, experience, and unlock new capabilities
- **Member Management**: Invite/remove system with role assignments and contribution tracking

## Ship Mechanics
- **Ship Types**: 5 ship classes from Dinghy to Legendary vessels with unique stats
- **Upgrade System**: 8+ ship upgrades improving durability, speed, cargo, and firepower
- **Ship Combat**: Integrated with PvP/PvE systems for naval battles
- **Customization**: Ship naming, figurehead, sail colors, and jolly roger design

## Combat Systems
- **PvP Combat**: Player vs player challenges with strategic turn-based mechanics
- **PvE Exploration**: Location-based enemy encounters with scaled difficulty
- **Combat Mechanics**: Attack, defend, special abilities, and flee options
- **Rewards System**: Experience, berry, bounty, and item rewards based on performance
- **Battle Cooldowns**: Prevents spam and encourages strategic timing

## Quest System - East Blue Saga
- **6 Story Arcs**: Romance Dawn, Orange Town, Syrup Village, Baratie, Arlong Park, Loguetown
- **Choice-driven Narratives**: Player decisions affect story outcomes and rewards
- **Origin-specific Content**: Different quest paths based on character background
- **Objective System**: Multi-step quests with progress tracking
- **Faction Integration**: Quest choices affect reputation with different factions

## Ally Recruitment
- **Canonical Characters**: Recruit famous One Piece characters as allies
- **Rarity System**: Common to Legendary allies with scaling bonuses
- **Bond Progression**: Ally relationships improve through use and interaction
- **Stat Bonuses**: Allies provide passive bonuses to character stats
- **Special Abilities**: Active and passive abilities unique to each ally

## Faction & Reputation
- **5 Major Factions**: Pirate, Marine, Revolutionary, World Government, Neutral
- **Dynamic Reputation**: Actions affect standing with multiple factions simultaneously
- **Rank Progression**: Faction-specific rank systems with unique titles and benefits
- **Faction Benefits**: Reputation unlocks bonuses, discounts, and special abilities
- **Alignment System**: Ally, Friendly, Neutral, Hostile, Enemy standings

## Command Structure
- **Character Commands**: create_character, character, characters, races, origins, dreams
- **Crew Commands**: create_crew, crew, crew_invite, crew_leave
- **Ship Commands**: ship, ship_upgrade, ship_repair
- **Combat Commands**: challenge (PvP), explore (PvE)
- **Quest Commands**: quests, quest_info, quest_start, quest_progress
- **Ally Commands**: allies, ally_recruit, ally_info
- **Reputation Commands**: reputation, faction_info, faction_ranks

## Configuration Management
- **Centralized Config**: Single configuration class managing bot settings, file paths, and game balance
- **Environment Variables**: Secure token management through environment variables
- **Modular Settings**: Separate configuration sections for different game aspects (XP, limits, colors)

# External Dependencies

## Discord Integration
- **Discord.py Library**: Primary framework for Discord bot functionality and API interaction
- **Discord Developer Portal**: Bot registration and permission management

## Data Storage
- **Local JSON Files**: Character data persistence in `data/characters.json`
- **File System**: Local directory structure for data organization

## Runtime Environment
- **Python 3.x**: Core runtime environment
- **Asyncio**: Asynchronous programming support for concurrent operations
- **Logging Module**: Built-in Python logging for debugging and monitoring

## Development Dependencies
- **Environment Variables**: `DISCORD_BOT_TOKEN` for bot authentication
- **File Permissions**: Read/write access to local data directory