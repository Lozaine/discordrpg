"""
PvP and PvE combat system commands
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Dict, List
import random
import asyncio
import logging
from datetime import datetime, timedelta

from ..utils.embeds import create_embed
from config import Config

logger = logging.getLogger(__name__)

class CombatCog(commands.Cog):
    """Combat system commands for PvP and PvE"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_battles = {}  # Track ongoing battles
        self.battle_cooldowns = {}  # Track battle cooldowns
    
    @app_commands.command(name="challenge", description="Challenge another player to PvP combat")
    @app_commands.describe(opponent="The player you want to challenge")
    async def challenge_pvp(self, interaction: discord.Interaction, opponent: discord.Member):
        """Challenge another player to PvP combat"""
        await interaction.response.defer()
        
        challenger_id = str(interaction.user.id)
        opponent_id = str(opponent.id)
        
        try:
            # Prevent self-challenge
            if challenger_id == opponent_id:
                embed = create_embed(
                    "Invalid Challenge",
                    "❌ You cannot challenge yourself to combat!",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Check if both players have characters
            challenger_chars = self.bot.data_manager.get_user_characters(challenger_id)
            opponent_chars = self.bot.data_manager.get_user_characters(opponent_id)
            
            if not challenger_chars:
                embed = create_embed(
                    "No Character",
                    "❌ You need to create a character first.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            if not opponent_chars:
                embed = create_embed(
                    "Opponent No Character",
                    f"❌ {opponent.display_name} doesn't have a character yet.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            challenger_char = challenger_chars[0]
            opponent_char = opponent_chars[0]
            
            # Check cooldowns
            if self._check_battle_cooldown(challenger_id):
                embed = create_embed(
                    "Cooldown Active",
                    "❌ You must wait before challenging another player.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            if self._check_battle_cooldown(opponent_id):
                embed = create_embed(
                    "Opponent Cooldown",
                    f"❌ {opponent.display_name} is on battle cooldown.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Check if either player is already in battle
            if challenger_id in self.active_battles or opponent_id in self.active_battles:
                embed = create_embed(
                    "Battle in Progress",
                    "❌ One of you is already in battle.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create challenge embed
            embed = discord.Embed(
                title="⚔️ PvP Challenge!",
                description=f"**{challenger_char.name}** has challenged **{opponent_char.name}** to combat!",
                color=Config.EMBED_COLORS["warning"]
            )
            
            # Add character stats
            challenger_stats = challenger_char.get_total_stats()
            opponent_stats = opponent_char.get_total_stats()
            
            embed.add_field(
                name=f"⚔️ {challenger_char.name}",
                value=f"**Level:** {challenger_char.level}\n"
                      f"**Race:** {challenger_char.race}\n"
                      f"**Power:** {sum(challenger_stats.values())}",
                inline=True
            )
            
            embed.add_field(
                name=f"🛡️ {opponent_char.name}",
                value=f"**Level:** {opponent_char.level}\n"
                      f"**Race:** {opponent_char.race}\n"
                      f"**Power:** {sum(opponent_stats.values())}",
                inline=True
            )
            
            embed.add_field(
                name="💰 Stakes",
                value=f"**Winner gets:** 25% of loser's berry\n"
                      f"**Experience:** 200 XP for winner\n"
                      f"**Bounty:** +5,000,000 for winner",
                inline=False
            )
            
            # Create accept/decline view
            view = PvPChallengeView(challenger_id, opponent_id, challenger_char, opponent_char, self)
            
            await interaction.followup.send(f"{opponent.mention}", embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error in PvP challenge: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while creating the challenge.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="explore", description="Explore and encounter enemies for PvE combat")
    @app_commands.describe(location="Choose a location to explore")
    async def explore_pve(self, interaction: discord.Interaction, location: str):
        """Start PvE exploration and combat"""
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        try:
            # Check if player has character
            user_characters = self.bot.data_manager.get_user_characters(user_id)
            if not user_characters:
                embed = create_embed(
                    "No Character",
                    "❌ You need to create a character first.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            character = user_characters[0]
            
            # Check if already in battle
            if user_id in self.active_battles:
                embed = create_embed(
                    "Battle in Progress",
                    "❌ You are already in combat!",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Check exploration cooldown
            if self._check_battle_cooldown(user_id):
                embed = create_embed(
                    "Exploration Cooldown",
                    "❌ You must rest before exploring again.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Generate enemy based on location and character level
            enemy = self._generate_enemy(location, character.level)
            
            # Start PvE battle
            battle = PvEBattle(character, enemy, location)
            self.active_battles[user_id] = battle
            
            # Create battle embed
            embed = discord.Embed(
                title=f"🗺️ Exploring {location}",
                description=f"**{character.name}** encounters **{enemy['name']}**!",
                color=Config.EMBED_COLORS["warning"]
            )
            
            embed.add_field(
                name=f"⚔️ {character.name}",
                value=f"**Level:** {character.level}\n"
                      f"**HP:** {battle.player_hp}/{battle.player_max_hp}\n"
                      f"**Power:** {sum(character.get_total_stats().values())}",
                inline=True
            )
            
            embed.add_field(
                name=f"👹 {enemy['name']}",
                value=f"**Level:** {enemy['level']}\n"
                      f"**HP:** {battle.enemy_hp}/{battle.enemy_max_hp}\n"
                      f"**Type:** {enemy['type']}",
                inline=True
            )
            
            embed.add_field(
                name="💰 Potential Rewards",
                value=f"**Experience:** {enemy['xp_reward']} XP\n"
                      f"**Berry:** ฿{enemy['berry_reward']:,}\n"
                      f"**Items:** {', '.join(enemy['item_rewards'])}",
                inline=False
            )
            
            # Create battle action view
            view = PvEBattleView(user_id, battle, self)
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error in PvE exploration: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred during exploration.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    def _check_battle_cooldown(self, user_id: str) -> bool:
        """Check if user is on battle cooldown"""
        if user_id in self.battle_cooldowns:
            cooldown_end = self.battle_cooldowns[user_id]
            if datetime.now() < cooldown_end:
                return True
            else:
                del self.battle_cooldowns[user_id]
        return False
    
    def _set_battle_cooldown(self, user_id: str, minutes: int = 5):
        """Set battle cooldown for user"""
        self.battle_cooldowns[user_id] = datetime.now() + timedelta(minutes=minutes)
    
    def _generate_enemy(self, location: str, player_level: int) -> Dict:
        """Generate an enemy based on location and player level"""
        enemies_by_location = {
            "East Blue": [
                {"name": "Pirate Thug", "type": "Human Pirate", "difficulty": 0.8},
                {"name": "Marine Soldier", "type": "Marine", "difficulty": 1.0},
                {"name": "Bandit", "type": "Criminal", "difficulty": 0.7},
                {"name": "Sea King (Small)", "type": "Sea Monster", "difficulty": 1.5}
            ],
            "Grand Line": [
                {"name": "Veteran Pirate", "type": "Experienced Fighter", "difficulty": 1.2},
                {"name": "Baroque Works Agent", "type": "Assassin", "difficulty": 1.4},
                {"name": "Giant Warrior", "type": "Giant", "difficulty": 2.0},
                {"name": "Devil Fruit User", "type": "Power User", "difficulty": 1.8}
            ],
            "New World": [
                {"name": "Yonko Subordinate", "type": "Elite Pirate", "difficulty": 2.5},
                {"name": "Marine Vice Admiral", "type": "High-Ranking Marine", "difficulty": 2.8},
                {"name": "CP9 Agent", "type": "Government Assassin", "difficulty": 3.0},
                {"name": "Sea King (Large)", "type": "Ancient Beast", "difficulty": 3.5}
            ]
        }
        
        location_enemies = enemies_by_location.get(location, enemies_by_location["East Blue"])
        enemy_template = random.choice(location_enemies)
        
        # Scale enemy to player level
        enemy_level = max(1, player_level + random.randint(-2, 2))
        difficulty_modifier = enemy_template["difficulty"]
        
        enemy = {
            "name": enemy_template["name"],
            "type": enemy_template["type"],
            "level": enemy_level,
            "difficulty": difficulty_modifier,
            "hp": int(50 + (enemy_level * 20) * difficulty_modifier),
            "attack": int(10 + (enemy_level * 5) * difficulty_modifier),
            "defense": int(5 + (enemy_level * 3) * difficulty_modifier),
            "xp_reward": int(50 + (enemy_level * 25) * difficulty_modifier),
            "berry_reward": int(1000 + (enemy_level * 500) * difficulty_modifier),
            "item_rewards": self._generate_enemy_drops(enemy_template["type"], enemy_level)
        }
        
        return enemy
    
    def _generate_enemy_drops(self, enemy_type: str, level: int) -> List[str]:
        """Generate random item drops for defeated enemies"""
        possible_drops = {
            "Human Pirate": ["Rusty Sword", "Pirate Bandana", "Treasure Map Fragment"],
            "Marine": ["Marine Badge", "Standard Sword", "Justice Medal"],
            "Criminal": ["Stolen Goods", "Lockpicks", "Bounty Poster"],
            "Sea Monster": ["Sea King Meat", "Monster Scale", "Ancient Bone"],
            "Giant": ["Giant's Club", "Warrior's Honor", "Elbaf Steel"],
            "Power User": ["Devil Fruit Guide", "Power Essence", "Rare Material"]
        }
        
        drops = possible_drops.get(enemy_type, ["Basic Item"])
        num_drops = random.randint(1, min(3, max(1, level // 5)))
        
        return random.sample(drops, min(num_drops, len(drops)))

class PvEBattle:
    """Represents a PvE battle instance"""
    
    def __init__(self, character, enemy, location):
        self.character = character
        self.enemy = enemy
        self.location = location
        
        # Battle state
        character_stats = character.get_total_stats()
        self.player_max_hp = 100 + (character.level * 20) + character_stats.get("durability", 0) * 5
        self.player_hp = self.player_max_hp
        self.player_attack = 20 + (character.level * 3) + character_stats.get("strength", 0) * 2
        self.player_defense = 10 + (character.level * 2) + character_stats.get("durability", 0)
        
        self.enemy_max_hp = enemy["hp"]
        self.enemy_hp = enemy["hp"]
        self.enemy_attack = enemy["attack"]
        self.enemy_defense = enemy["defense"]
        
        self.turn = "player"
        self.battle_log = []

class PvEBattleView(discord.ui.View):
    """Battle interface for PvE combat"""
    
    def __init__(self, user_id: str, battle: PvEBattle, combat_cog):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.battle = battle
        self.combat_cog = combat_cog
    
    @discord.ui.button(label="Attack", style=discord.ButtonStyle.red, emoji="⚔️")
    async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ This is not your battle!", ephemeral=True)
            return
        
        await self._execute_battle_turn(interaction, "attack")
    
    @discord.ui.button(label="Defend", style=discord.ButtonStyle.grey, emoji="🛡️")
    async def defend(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ This is not your battle!", ephemeral=True)
            return
        
        await self._execute_battle_turn(interaction, "defend")
    
    @discord.ui.button(label="Special Attack", style=discord.ButtonStyle.blurple, emoji="💥")
    async def special_attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ This is not your battle!", ephemeral=True)
            return
        
        await self._execute_battle_turn(interaction, "special")
    
    @discord.ui.button(label="Flee", style=discord.ButtonStyle.grey, emoji="🏃")
    async def flee(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("❌ This is not your battle!", ephemeral=True)
            return
        
        # Chance to escape based on agility
        character_stats = self.battle.character.get_total_stats()
        escape_chance = 0.5 + (character_stats.get("agility", 0) * 0.02)
        
        if random.random() < escape_chance:
            # Successful escape
            del self.combat_cog.active_battles[self.user_id]
            self.combat_cog._set_battle_cooldown(self.user_id, 2)  # Short cooldown for fleeing
            
            embed = discord.Embed(
                title="🏃 Escaped!",
                description=f"**{self.battle.character.name}** successfully escaped from **{self.battle.enemy['name']}**!",
                color=Config.EMBED_COLORS["warning"]
            )
            
            for item in self.children:
                item.disabled = True
            
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            # Failed escape - enemy gets free attack
            await self._execute_battle_turn(interaction, "flee_failed")
    
    async def _execute_battle_turn(self, interaction: discord.Interaction, action: str):
        """Execute a battle turn"""
        battle = self.battle
        
        # Player action
        if action == "attack":
            damage = random.randint(int(battle.player_attack * 0.8), int(battle.player_attack * 1.2))
            damage = max(1, damage - battle.enemy_defense // 2)
            battle.enemy_hp = max(0, battle.enemy_hp - damage)
            battle.battle_log.append(f"⚔️ {battle.character.name} attacks for {damage} damage!")
        
        elif action == "defend":
            battle.battle_log.append(f"🛡️ {battle.character.name} takes a defensive stance!")
            # Defense will reduce incoming damage this turn
        
        elif action == "special":
            # Special attack based on character race or dream
            special_damage = int(battle.player_attack * 1.5)
            damage = max(1, special_damage - battle.enemy_defense // 2)
            battle.enemy_hp = max(0, battle.enemy_hp - damage)
            
            special_name = self._get_special_attack_name(battle.character)
            battle.battle_log.append(f"💥 {battle.character.name} uses {special_name} for {damage} damage!")
        
        elif action == "flee_failed":
            battle.battle_log.append(f"🏃 {battle.character.name} failed to escape!")
        
        # Check if enemy is defeated
        if battle.enemy_hp <= 0:
            await self._handle_victory(interaction)
            return
        
        # Enemy turn (if player didn't flee successfully)
        if action != "flee":
            enemy_damage = random.randint(int(battle.enemy_attack * 0.7), int(battle.enemy_attack * 1.3))
            
            # Apply defense reduction
            if action == "defend":
                enemy_damage = max(1, enemy_damage // 2)
            else:
                enemy_damage = max(1, enemy_damage - battle.player_defense // 3)
            
            battle.player_hp = max(0, battle.player_hp - enemy_damage)
            battle.battle_log.append(f"👹 {battle.enemy['name']} attacks for {enemy_damage} damage!")
        
        # Check if player is defeated
        if battle.player_hp <= 0:
            await self._handle_defeat(interaction)
            return
        
        # Update battle display
        await self._update_battle_display(interaction)
    
    def _get_special_attack_name(self, character) -> str:
        """Get special attack name based on character"""
        special_attacks = {
            "Human": "Determination Strike",
            "Fish-Man": "Fish-Man Karate",
            "Mink": "Electro",
            "Skypiean": "Dial Attack",
            "Giant": "Giant's Strength"
        }
        return special_attacks.get(character.race, "Special Attack")
    
    async def _update_battle_display(self, interaction: discord.Interaction):
        """Update the battle display"""
        battle = self.battle
        
        embed = discord.Embed(
            title=f"⚔️ Battle in {battle.location}",
            description=f"**{battle.character.name}** vs **{battle.enemy['name']}**",
            color=Config.EMBED_COLORS["warning"]
        )
        
        # Player status
        player_hp_bar = self._create_hp_bar(battle.player_hp, battle.player_max_hp)
        embed.add_field(
            name=f"⚔️ {battle.character.name}",
            value=f"**HP:** {battle.player_hp}/{battle.player_max_hp}\n{player_hp_bar}",
            inline=True
        )
        
        # Enemy status
        enemy_hp_bar = self._create_hp_bar(battle.enemy_hp, battle.enemy_max_hp)
        embed.add_field(
            name=f"👹 {battle.enemy['name']}",
            value=f"**HP:** {battle.enemy_hp}/{battle.enemy_max_hp}\n{enemy_hp_bar}",
            inline=True
        )
        
        # Battle log
        if battle.battle_log:
            recent_log = battle.battle_log[-3:]  # Show last 3 actions
            embed.add_field(
                name="📜 Battle Log",
                value="\n".join(recent_log),
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    def _create_hp_bar(self, current_hp: int, max_hp: int) -> str:
        """Create a visual HP bar"""
        if max_hp == 0:
            return "▱▱▱▱▱▱▱▱▱▱"
        
        filled = int((current_hp / max_hp) * 10)
        empty = 10 - filled
        return "▰" * filled + "▱" * empty
    
    async def _handle_victory(self, interaction: discord.Interaction):
        """Handle player victory"""
        battle = self.battle
        character = battle.character
        enemy = battle.enemy
        
        # Remove from active battles
        del self.combat_cog.active_battles[self.user_id]
        self.combat_cog._set_battle_cooldown(self.user_id, 3)  # 3 minute cooldown after victory
        
        # Award rewards
        character.add_experience(enemy["xp_reward"])
        character.add_item("Berry", enemy["berry_reward"])
        
        for item in enemy["item_rewards"]:
            character.add_item(item, 1)
        
        # Save character
        self.combat_cog.bot.data_manager.save_character(character)
        
        # Create victory embed
        embed = discord.Embed(
            title="🏆 Victory!",
            description=f"**{character.name}** has defeated **{enemy['name']}**!",
            color=Config.EMBED_COLORS["success"]
        )
        
        embed.add_field(
            name="💰 Rewards Earned",
            value=f"**Experience:** +{enemy['xp_reward']} XP\n"
                  f"**Berry:** +฿{enemy['berry_reward']:,}\n"
                  f"**Items:** {', '.join(enemy['item_rewards'])}",
            inline=False
        )
        
        if character.level > 1:  # Check if leveled up
            embed.add_field(
                name="⭐ Level Up!",
                value=f"Congratulations! You are now level {character.level}!",
                inline=False
            )
        
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def _handle_defeat(self, interaction: discord.Interaction):
        """Handle player defeat"""
        battle = self.battle
        character = battle.character
        
        # Remove from active battles
        del self.combat_cog.active_battles[self.user_id]
        self.combat_cog._set_battle_cooldown(self.user_id, 10)  # 10 minute cooldown after defeat
        
        # Apply defeat penalties
        berry_loss = min(character.inventory.get("Berry", 0) // 4, 5000)  # Lose 25% of berry, max 5000
        if berry_loss > 0:
            character.remove_item("Berry", berry_loss)
        
        # Save character
        self.combat_cog.bot.data_manager.save_character(character)
        
        # Create defeat embed
        embed = discord.Embed(
            title="💀 Defeat!",
            description=f"**{character.name}** has been defeated by **{battle.enemy['name']}**!",
            color=Config.EMBED_COLORS["error"]
        )
        
        embed.add_field(
            name="💸 Penalties",
            value=f"**Berry Lost:** ฿{berry_loss:,}\n"
                  f"**Cooldown:** 10 minutes before next battle",
            inline=False
        )
        
        embed.add_field(
            name="💪 Keep Fighting!",
            value="Train harder and come back stronger!",
            inline=False
        )
        
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)

class PvPChallengeView(discord.ui.View):
    """View for PvP challenge acceptance"""
    
    def __init__(self, challenger_id: str, opponent_id: str, challenger_char, opponent_char, combat_cog):
        super().__init__(timeout=60)  # 1 minute to accept
        self.challenger_id = challenger_id
        self.opponent_id = opponent_id
        self.challenger_char = challenger_char
        self.opponent_char = opponent_char
        self.combat_cog = combat_cog
    
    @discord.ui.button(label="Accept Challenge", style=discord.ButtonStyle.green, emoji="⚔️")
    async def accept_challenge(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.opponent_id:
            await interaction.response.send_message("❌ This challenge is not for you!", ephemeral=True)
            return
        
        # Start PvP battle
        await self._start_pvp_battle(interaction)
    
    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, emoji="❌")
    async def decline_challenge(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.opponent_id:
            await interaction.response.send_message("❌ This challenge is not for you!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🚫 Challenge Declined",
            description=f"**{self.opponent_char.name}** has declined the challenge.",
            color=Config.EMBED_COLORS["error"]
        )
        
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def _start_pvp_battle(self, interaction: discord.Interaction):
        """Start the actual PvP battle"""
        # Simplified PvP battle resolution for now
        challenger_stats = self.challenger_char.get_total_stats()
        opponent_stats = self.opponent_char.get_total_stats()
        
        challenger_power = sum(challenger_stats.values()) + self.challenger_char.level * 10
        opponent_power = sum(opponent_stats.values()) + self.opponent_char.level * 10
        
        # Add some randomness to the outcome
        challenger_roll = random.randint(1, 100) + challenger_power
        opponent_roll = random.randint(1, 100) + opponent_power
        
        # Determine winner
        if challenger_roll > opponent_roll:
            winner = self.challenger_char
            loser = self.opponent_char
            winner_id = self.challenger_id
            loser_id = self.opponent_id
        else:
            winner = self.opponent_char
            loser = self.challenger_char
            winner_id = self.opponent_id
            loser_id = self.challenger_id
        
        # Apply rewards and penalties
        winner.add_experience(200)
        winner.add_bounty(5000000)
        
        berry_transfer = min(loser.inventory.get("Berry", 0) // 4, 10000)
        if berry_transfer > 0:
            loser.remove_item("Berry", berry_transfer)
            winner.add_item("Berry", berry_transfer)
        
        # Set cooldowns
        self.combat_cog._set_battle_cooldown(winner_id, 5)
        self.combat_cog._set_battle_cooldown(loser_id, 10)
        
        # Save characters
        self.combat_cog.bot.data_manager.save_character(winner)
        self.combat_cog.bot.data_manager.save_character(loser)
        
        # Create result embed
        embed = discord.Embed(
            title="🏆 PvP Battle Complete!",
            description=f"**{winner.name}** has defeated **{loser.name}** in combat!",
            color=Config.EMBED_COLORS["success"]
        )
        
        embed.add_field(
            name="🏆 Winner Rewards",
            value=f"**{winner.name}**\n"
                  f"• +200 Experience\n"
                  f"• +5,000,000 Bounty\n"
                  f"• +฿{berry_transfer:,} Berry",
            inline=True
        )
        
        embed.add_field(
            name="💸 Loser Penalties",
            value=f"**{loser.name}**\n"
                  f"• -฿{berry_transfer:,} Berry\n"
                  f"• 10 minute cooldown",
            inline=True
        )
        
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)