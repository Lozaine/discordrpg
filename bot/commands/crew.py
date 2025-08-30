"""
Crew management commands
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import logging

from ..models.crew import Crew, CrewMember, CREW_ROLES, get_available_roles
from ..models.ship import Ship, SHIP_TYPES
from ..utils.embeds import create_embed
from config import Config

logger = logging.getLogger(__name__)

class CrewCog(commands.Cog):
    """Crew management commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="create_crew", description="Create a new crew")
    @app_commands.describe(
        name="Name of your crew",
        description="Description of your crew",
        motto="Crew motto or slogan",
        flag="Crew flag emoji"
    )
    async def create_crew(
        self,
        interaction: discord.Interaction,
        name: str,
        description: Optional[str] = None,
        motto: Optional[str] = None,
        flag: Optional[str] = "🏴‍☠️"
    ):
        """Create a new crew"""
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        try:
            # Get user's active character
            user_characters = self.bot.data_manager.get_user_characters(user_id)
            if not user_characters:
                embed = create_embed(
                    "No Character",
                    "❌ You need to create a character first using `/create_character`.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            character = user_characters[0]  # Use first character
            
            # Check if user is already in a crew
            if character.crew_id:
                embed = create_embed(
                    "Already in Crew",
                    "❌ You are already a member of a crew. Leave your current crew first.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Check if character has completed first voyage (has a ship)
            if not self.bot.data_manager.get_character_ship(user_id, character.name):
                embed = create_embed(
                    "No Ship",
                    "❌ You need to complete your first voyage and obtain a ship before creating a crew.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create the crew
            crew = Crew(
                name=name,
                description=description or f"A crew led by {character.name}",
                motto=motto or "Adventure awaits!",
                flag_emoji=flag,
                faction=character.faction,
                captain_id=user_id
            )
            
            # Add creator as captain
            crew.add_member(user_id, character.name, "Captain")
            
            # Create basic ship for the crew
            ship = Ship(
                name=f"{name}'s Ship",
                ship_type="Caravel",
                description=f"The flagship of the {name} crew"
            )
            ship.upgrade_to_type("Caravel")
            
            # Save crew and ship
            self.bot.data_manager.save_crew(crew)
            self.bot.data_manager.save_ship(ship)
            
            # Update character with crew info
            character.crew_id = crew.crew_id
            crew.ship_id = ship.ship_id
            self.bot.data_manager.save_character(character)
            self.bot.data_manager.save_crew(crew)  # Update crew with ship ID
            
            # Create success embed
            embed = discord.Embed(
                title=f"{flag} Crew Created: {name}",
                description=f"**Captain:** {character.name}\n**Motto:** {crew.motto}",
                color=Config.EMBED_COLORS["success"]
            )
            
            embed.add_field(
                name="📋 Crew Info",
                value=f"**Members:** 1/{crew.get_max_members()}\n"
                      f"**Faction:** {crew.faction}\n"
                      f"**Ship:** {ship.name} ({ship.ship_type})",
                inline=True
            )
            
            embed.add_field(
                name="⚓ Next Steps",
                value="• Recruit crew members with `/crew invite`\n"
                      "• Upgrade your ship with `/ship upgrade`\n"
                      "• Start quests with `/quest start`",
                inline=True
            )
            
            embed.set_footer(text=f"Crew ID: {crew.crew_id}")
            
            await interaction.followup.send(embed=embed)
            logger.info(f"Crew created: {name} by {character.name} ({user_id})")
            
        except Exception as e:
            logger.error(f"Error creating crew: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while creating your crew.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="crew", description="View crew information")
    async def view_crew(self, interaction: discord.Interaction):
        """View current crew information"""
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        try:
            character = self.bot.data_manager.get_user_characters(user_id)[0]
            
            if not character.crew_id:
                embed = create_embed(
                    "No Crew",
                    "❌ You are not a member of any crew. Create one with `/create_crew` or join one with `/crew join`.",
                    "warning"
                )
                await interaction.followup.send(embed=embed)
                return
            
            crew = self.bot.data_manager.get_crew(character.crew_id)
            if not crew:
                embed = create_embed(
                    "Crew Not Found",
                    "❌ Your crew data could not be found.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Get ship info
            ship = None
            if crew.ship_id:
                ship = self.bot.data_manager.get_ship(crew.ship_id)
            
            # Create crew info embed
            embed = discord.Embed(
                title=f"{crew.flag_emoji} {crew.name}",
                description=f"*{crew.motto}*\n\n{crew.description}",
                color=Config.EMBED_COLORS["info"]
            )
            
            # Basic info
            captain = crew.get_captain()
            embed.add_field(
                name="📋 Crew Details",
                value=f"**Captain:** {captain.character_name if captain else 'Unknown'}\n"
                      f"**Faction:** {crew.faction}\n"
                      f"**Level:** {crew.level}\n"
                      f"**Members:** {len(crew.members)}/{crew.get_max_members()}",
                inline=True
            )
            
            # Crew stats
            embed.add_field(
                name="💰 Resources",
                value=f"**Total Bounty:** ฿{crew.total_bounty:,}\n"
                      f"**Treasury:** ฿{crew.treasury:,}\n"
                      f"**Reputation:** {crew.reputation}\n"
                      f"**Experience:** {crew.experience}/{crew.get_xp_for_next_level()}",
                inline=True
            )
            
            # Ship info
            if ship:
                embed.add_field(
                    name="⛵ Ship",
                    value=f"**Name:** {ship.name}\n"
                          f"**Type:** {ship.ship_type}\n"
                          f"**Durability:** {ship.durability}/{ship.max_durability}\n"
                          f"**Speed:** {ship.speed}",
                    inline=True
                )
            
            # Member list
            member_list = []
            for member in crew.members:
                role_emoji = CREW_ROLES.get(member.role, {}).get("emoji", "👤")
                member_list.append(f"{role_emoji} **{member.character_name}** - {member.role}")
            
            if member_list:
                embed.add_field(
                    name="👥 Crew Members",
                    value="\n".join(member_list),
                    inline=False
                )
            
            # Crew bonuses
            bonuses = crew.get_crew_bonuses()
            bonus_text = []
            for bonus_type, multiplier in bonuses.items():
                if multiplier > 1.0:
                    bonus_percent = int((multiplier - 1.0) * 100)
                    bonus_text.append(f"**{bonus_type.title()}:** +{bonus_percent}%")
            
            if bonus_text:
                embed.add_field(
                    name="⭐ Active Bonuses",
                    value="\n".join(bonus_text),
                    inline=False
                )
            
            embed.set_footer(text=f"Created on {crew.created_at.strftime('%B %d, %Y')}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error viewing crew: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while retrieving crew information.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="crew_invite", description="Invite a player to your crew")
    @app_commands.describe(user="The user to invite to your crew")
    async def invite_to_crew(self, interaction: discord.Interaction, user: discord.Member):
        """Invite a user to join the crew"""
        await interaction.response.defer()
        
        inviter_id = str(interaction.user.id)
        invitee_id = str(user.id)
        
        try:
            # Get inviter's character and crew
            inviter_character = self.bot.data_manager.get_user_characters(inviter_id)[0]
            if not inviter_character.crew_id:
                embed = create_embed(
                    "No Crew",
                    "❌ You need to be in a crew to invite others.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            crew = self.bot.data_manager.get_crew(inviter_character.crew_id)
            
            # Check if inviter has permission (Captain or First Mate)
            inviter_member = crew.get_member(inviter_id)
            if inviter_member.role not in ["Captain", "First Mate"]:
                embed = create_embed(
                    "No Permission",
                    "❌ Only the Captain or First Mate can invite new crew members.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Check if crew is full
            if len(crew.members) >= crew.get_max_members():
                embed = create_embed(
                    "Crew Full",
                    f"❌ Your crew is full ({len(crew.members)}/{crew.get_max_members()} members).",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Check if invitee has a character
            invitee_characters = self.bot.data_manager.get_user_characters(invitee_id)
            if not invitee_characters:
                embed = create_embed(
                    "No Character",
                    f"❌ {user.display_name} needs to create a character first.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            invitee_character = invitee_characters[0]
            
            # Check if invitee is already in a crew
            if invitee_character.crew_id:
                embed = create_embed(
                    "Already in Crew",
                    f"❌ {user.display_name} is already a member of another crew.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Create invitation embed
            embed = discord.Embed(
                title=f"{crew.flag_emoji} Crew Invitation",
                description=f"**{inviter_character.name}** has invited **{invitee_character.name}** to join **{crew.name}**!",
                color=Config.EMBED_COLORS["info"]
            )
            
            embed.add_field(
                name="📋 Crew Info",
                value=f"**Faction:** {crew.faction}\n"
                      f"**Members:** {len(crew.members)}/{crew.get_max_members()}\n"
                      f"**Level:** {crew.level}\n"
                      f"**Motto:** {crew.motto}",
                inline=False
            )
            
            # Create accept/decline buttons
            view = CrewInviteView(crew.crew_id, invitee_id, invitee_character.name)
            
            await interaction.followup.send(f"{user.mention}", embed=embed, view=view)
            
        except Exception as e:
            logger.error(f"Error inviting to crew: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while sending the crew invitation.",
                "error"
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="crew_leave", description="Leave your current crew")
    async def leave_crew(self, interaction: discord.Interaction):
        """Leave the current crew"""
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        
        try:
            character = self.bot.data_manager.get_user_characters(user_id)[0]
            
            if not character.crew_id:
                embed = create_embed(
                    "No Crew",
                    "❌ You are not a member of any crew.",
                    "error"
                )
                await interaction.followup.send(embed=embed)
                return
            
            crew = self.bot.data_manager.get_crew(character.crew_id)
            member = crew.get_member(user_id)
            
            # Check if user is the captain
            if member.role == "Captain":
                if len(crew.members) > 1:
                    embed = create_embed(
                        "Cannot Leave",
                        "❌ As captain, you cannot leave the crew while there are other members. Transfer leadership first or disband the crew.",
                        "error"
                    )
                    await interaction.followup.send(embed=embed)
                    return
                else:
                    # Captain leaving alone - disband crew
                    self.bot.data_manager.delete_crew(crew.crew_id)
                    character.crew_id = ""
                    self.bot.data_manager.save_character(character)
                    
                    embed = create_embed(
                        "Crew Disbanded",
                        f"✅ You have left and disbanded the **{crew.name}** crew.",
                        "success"
                    )
                    await interaction.followup.send(embed=embed)
                    return
            
            # Remove member from crew
            crew.remove_member(user_id)
            character.crew_id = ""
            
            # Save changes
            self.bot.data_manager.save_crew(crew)
            self.bot.data_manager.save_character(character)
            
            embed = create_embed(
                "Left Crew",
                f"✅ You have left the **{crew.name}** crew.",
                "success"
            )
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error leaving crew: {e}")
            embed = create_embed(
                "Error",
                "❌ An error occurred while leaving the crew.",
                "error"
            )
            await interaction.followup.send(embed=embed)

class CrewInviteView(discord.ui.View):
    """View for crew invitation buttons"""
    
    def __init__(self, crew_id: str, invitee_id: str, character_name: str):
        super().__init__(timeout=300)  # 5 minutes
        self.crew_id = crew_id
        self.invitee_id = invitee_id
        self.character_name = character_name
    
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, emoji="✅")
    async def accept_invite(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.invitee_id:
            await interaction.response.send_message("❌ This invitation is not for you.", ephemeral=True)
            return
        
        try:
            # Get the bot instance through the interaction
            bot = interaction.client
            
            # Get crew and character
            crew = bot.data_manager.get_crew(self.crew_id)
            character = bot.data_manager.get_user_characters(self.invitee_id)[0]
            
            # Check if crew still exists and has space
            if not crew or len(crew.members) >= crew.get_max_members():
                await interaction.response.send_message("❌ This crew invitation is no longer valid.", ephemeral=True)
                return
            
            # Check if character is still available
            if character.crew_id:
                await interaction.response.send_message("❌ You are already in a crew.", ephemeral=True)
                return
            
            # Add member to crew
            crew.add_member(self.invitee_id, self.character_name, "Fighter")
            character.crew_id = crew.crew_id
            
            # Save changes
            bot.data_manager.save_crew(crew)
            bot.data_manager.save_character(character)
            
            # Update embed
            embed = discord.Embed(
                title=f"{crew.flag_emoji} Invitation Accepted!",
                description=f"**{self.character_name}** has joined **{crew.name}**!",
                color=Config.EMBED_COLORS["success"]
            )
            
            # Disable buttons
            for item in self.children:
                item.disabled = True
            
            await interaction.response.edit_message(embed=embed, view=self)
            
        except Exception as e:
            logger.error(f"Error accepting crew invite: {e}")
            await interaction.response.send_message("❌ An error occurred while joining the crew.", ephemeral=True)
    
    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red, emoji="❌")
    async def decline_invite(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.invitee_id:
            await interaction.response.send_message("❌ This invitation is not for you.", ephemeral=True)
            return
        
        # Update embed
        embed = discord.Embed(
            title="🚫 Invitation Declined",
            description=f"**{self.character_name}** has declined the crew invitation.",
            color=Config.EMBED_COLORS["error"]
        )
        
        # Disable buttons
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)