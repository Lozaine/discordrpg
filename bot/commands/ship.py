"""
Ship management and upgrade commands
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import logging

from ..models.ship import Ship, SHIP_TYPES, SHIP_UPGRADES, calculate_upgrade_cost
from ..utils.embeds import create_embed
from config import Config

logger = logging.getLogger(__name__)

class ShipCog(commands.Cog):
    """Ship management commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="ship", description="View your crew's ship information")
    async def view_ship(self, interaction: discord.Interaction):
        """View current ship information"""
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        try:
            # Get user's character
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
            
            # Get character's ship through crew
            ship = self.bot.data_manager.get_character_ship(user_id, character.name)
            if not ship:
                embed = create_embed(
                    "No Ship",
                    "❌ You don't have a ship yet. Join a crew or complete quests to obtain one.",
                    "warning"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Get ship type info
            ship_type_data = SHIP_TYPES.get(ship.ship_type, {})
            ship_emoji = ship_type_data.get("emoji", "⛵")
            
            # Create ship info embed
            embed = discord.Embed(
                title=f"{ship_emoji} {ship.name}",
                description=f"*{ship.description}*\n\n**Type:** {ship.ship_type}",
                color=Config.EMBED_COLORS["info"]
            )
            
            # Ship stats
            total_stats = ship.get_total_stats()
            embed.add_field(
                name="📊 Ship Stats",
                value=f"**Durability:** {ship.durability}/{total_stats['durability']}\n"
                      f"**Speed:** {total_stats['speed']}\n"
                      f"**Cargo:** {sum(ship.cargo.values())}/{total_stats['cargo_capacity']}\n"
                      f"**Crew Capacity:** {total_stats['crew_capacity']}\n"
                      f"**Firepower:** {total_stats['firepower']}",
                inline=True
            )
            
            # Ship features
            features = []
            if ship.upgrades:
                for upgrade_id in ship.upgrades:
                    upgrade = SHIP_UPGRADES.get(upgrade_id)
                    if upgrade:
                        features.append(f"⭐ {upgrade.name}")
            
            if ship.special_features:
                features.extend([f"✨ {feature}" for feature in ship.special_features])
            
            if features:
                embed.add_field(
                    name="🔧 Installed Upgrades",
                    value="\n".join(features) if features else "None",
                    inline=True
                )
            
            # Ship customization
            embed.add_field(
                name="🎨 Customization",
                value=f"**Figurehead:** {ship.figurehead or 'None'}\n"
                      f"**Sail Color:** {ship.sail_color}\n"
                      f"**Jolly Roger:** {ship.jolly_roger}",
                inline=True
            )
            
            # Ship history
            embed.add_field(
                name="🏴‍☠️ Battle Record",
                value=f"**Victories:** {ship.battles_won}\n"
                      f"**Defeats:** {ship.battles_lost}\n"
                      f"**Distance Sailed:** {ship.distance_traveled:,} nautical miles",
                inline=True
            )
            
            # Cargo
            if ship.cargo:
                cargo_list = []
                for item, quantity in ship.cargo.items():
                    cargo_list.append(f"• {item}: {quantity}")
                
                embed.add_field(
                    name="📦 Cargo Hold",
                    value="\n".join(cargo_list) if cargo_list else "Empty",
                    inline=True
                )
            
            embed.set_footer(text=f"Last repaired: {ship.last_repaired.strftime('%B %d, %Y')}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error viewing ship: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while retrieving ship information.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="ship_upgrade", description="Upgrade your ship with new features")
    async def upgrade_ship(self, interaction: discord.Interaction):
        """Show available ship upgrades"""
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        try:
            # Get user's character and ship
            character = self.bot.data_manager.get_user_characters(user_id)[0]
            ship = self.bot.data_manager.get_character_ship(user_id, character.name)
            
            if not ship:
                embed = create_embed(
                    "No Ship",
                    "❌ You don't have a ship to upgrade.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Get crew for level check
            crew = None
            if character.crew_id:
                crew = self.bot.data_manager.get_crew(character.crew_id)
            
            crew_level = crew.level if crew else 1
            
            # Get available upgrades
            available_upgrades = []
            for upgrade_id, upgrade in SHIP_UPGRADES.items():
                if ship.can_upgrade(upgrade_id, crew_level):
                    cost = calculate_upgrade_cost(ship, upgrade_id)
                    available_upgrades.append((upgrade_id, upgrade, cost))
            
            if not available_upgrades:
                embed = create_embed(
                    "No Upgrades Available",
                    "❌ No ship upgrades are currently available. Increase your crew level or complete prerequisites.",
                    "warning"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create upgrade selection embed
            embed = discord.Embed(
                title=f"⚙️ Ship Upgrades for {ship.name}",
                description="Choose an upgrade to install on your ship:",
                color=Config.EMBED_COLORS["info"]
            )
            
            # Add available upgrades
            for i, (upgrade_id, upgrade, cost) in enumerate(available_upgrades[:5]):  # Limit to 5
                embed.add_field(
                    name=f"{i+1}. {upgrade.name}",
                    value=f"**Type:** {upgrade.upgrade_type.title()}\n"
                          f"**Cost:** ฿{cost:,}\n"
                          f"**Effect:** {upgrade.description}",
                    inline=False
                )
            
            # Create upgrade selection view
            view = ShipUpgradeView(user_id, ship, available_upgrades, self.bot)
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error showing ship upgrades: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while loading upgrades.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="ship_repair", description="Repair your ship's damage")
    async def repair_ship(self, interaction: discord.Interaction):
        """Repair ship damage"""
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        try:
            # Get user's character and ship
            character = self.bot.data_manager.get_user_characters(user_id)[0]
            ship = self.bot.data_manager.get_character_ship(user_id, character.name)
            
            if not ship:
                embed = create_embed(
                    "No Ship",
                    "❌ You don't have a ship to repair.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Check if ship needs repair
            if ship.durability >= ship.max_durability:
                embed = create_embed(
                    "Ship Undamaged",
                    "✅ Your ship is already in perfect condition!",
                    "success"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Calculate repair cost
            damage = ship.max_durability - ship.durability
            repair_cost = damage * 100  # 100 berry per durability point
            
            # Check if player has enough money
            character_berry = character.inventory.get("Berry", 0)
            if character_berry < repair_cost:
                embed = create_embed(
                    "Insufficient Funds",
                    f"❌ You need ฿{repair_cost:,} to fully repair your ship, but you only have ฿{character_berry:,}.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Perform repair
            repaired = ship.repair()
            character.remove_item("Berry", repair_cost)
            
            # Save changes
            self.bot.data_manager.save_ship(ship)
            self.bot.data_manager.save_character(character)
            
            embed = discord.Embed(
                title="🔧 Ship Repaired!",
                description=f"Your ship **{ship.name}** has been fully repaired!",
                color=Config.EMBED_COLORS["success"]
            )
            
            embed.add_field(
                name="🛠️ Repair Details",
                value=f"**Durability Restored:** {repaired}\n"
                      f"**Cost:** ฿{repair_cost:,}\n"
                      f"**Current Durability:** {ship.durability}/{ship.max_durability}",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error repairing ship: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while repairing the ship.",
                "error"
            )
            await interaction.followup.send(embed=embed)

class ShipUpgradeView(discord.ui.View):
    """View for selecting ship upgrades"""
    
    def __init__(self, user_id: str, ship: Ship, available_upgrades: list, bot):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.ship = ship
        self.available_upgrades = available_upgrades
        self.bot = bot
        
        # Add upgrade buttons
        for i, (upgrade_id, upgrade, cost) in enumerate(available_upgrades[:5]):
            button = discord.ui.Button(
                label=f"{i+1}. {upgrade.name}",
                style=discord.ButtonStyle.blurple,
                custom_id=f"upgrade_{upgrade_id}"
            )
            button.callback = self.create_upgrade_callback(upgrade_id, upgrade, cost)
            self.add_item(button)
    
    def create_upgrade_callback(self, upgrade_id: str, upgrade, cost: int):
        """Create callback for upgrade button"""
        async def upgrade_callback(interaction: discord.Interaction):
            if str(interaction.user.id) != self.user_id:
                await interaction.response.send_message("❌ This is not your ship upgrade menu!", ephemeral=True)
                return
            
            try:
                # Get current character
                character = self.bot.data_manager.get_user_characters(self.user_id)[0]
                
                # Check if player has enough money
                character_berry = character.inventory.get("Berry", 0)
                if character_berry < cost:
                    await interaction.response.send_message(
                        f"❌ You need ฿{cost:,} but only have ฿{character_berry:,}.",
                        ephemeral=True
                    )
                    return
                
                # Apply upgrade
                self.ship.add_upgrade(upgrade_id)
                character.remove_item("Berry", cost)
                
                # Save changes
                self.bot.data_manager.save_ship(self.ship)
                self.bot.data_manager.save_character(character)
                
                # Create success embed
                embed = discord.Embed(
                    title="⚙️ Upgrade Installed!",
                    description=f"**{upgrade.name}** has been installed on **{self.ship.name}**!",
                    color=Config.EMBED_COLORS["success"]
                )
                
                embed.add_field(
                    name="🔧 Upgrade Details",
                    value=f"**Type:** {upgrade.upgrade_type.title()}\n"
                          f"**Cost:** ฿{cost:,}\n"
                          f"**Effect:** {upgrade.description}",
                    inline=False
                )
                
                # Show stat bonuses
                if upgrade.stats_bonus:
                    bonus_text = []
                    for stat, bonus in upgrade.stats_bonus.items():
                        bonus_text.append(f"**{stat.title()}:** +{bonus}")
                    
                    embed.add_field(
                        name="📊 Stat Bonuses",
                        value="\n".join(bonus_text),
                        inline=False
                    )
                
                # Disable all buttons
                for item in self.children:
                    item.disabled = True
                
                await interaction.response.edit_message(embed=embed, view=self)
                
                logger.info(f"Ship upgrade {upgrade_id} installed for {character.name}")
                
            except Exception as e:
                logger.error(f"Error installing ship upgrade: {e}")
                await interaction.response.send_message(
                    "❌ An error occurred while installing the upgrade.",
                    ephemeral=True
                )
        
        return upgrade_callback