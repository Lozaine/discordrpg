"""
Faction and reputation system
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class FactionAlignment(Enum):
    ALLY = "ally"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    HOSTILE = "hostile"
    ENEMY = "enemy"

@dataclass
class FactionReputation:
    """Player's reputation with a specific faction"""
    user_id: str
    character_name: str
    faction_name: str
    reputation: int = 0  # Can be negative
    rank: str = "Unknown"
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Reputation milestones and achievements
    milestones_reached: List[str] = field(default_factory=list)
    faction_quests_completed: int = 0
    faction_conflicts_won: int = 0
    
    def get_alignment(self) -> FactionAlignment:
        """Get faction alignment based on reputation"""
        if self.reputation >= 500:
            return FactionAlignment.ALLY
        elif self.reputation >= 200:
            return FactionAlignment.FRIENDLY
        elif self.reputation >= -200:
            return FactionAlignment.NEUTRAL
        elif self.reputation >= -500:
            return FactionAlignment.HOSTILE
        else:
            return FactionAlignment.ENEMY
    
    def get_rank_title(self) -> str:
        """Get faction-specific rank title"""
        faction_ranks = FACTION_RANKS.get(self.faction_name, {})
        
        for min_rep, rank_info in sorted(faction_ranks.items(), reverse=True):
            if self.reputation >= min_rep:
                return rank_info["title"]
        
        return "Unknown"
    
    def add_reputation(self, amount: int, reason: str = "") -> List[str]:
        """Add reputation and return any new milestones reached"""
        old_reputation = self.reputation
        self.reputation += amount
        self.last_updated = datetime.now()
        
        # Check for new milestones
        new_milestones = []
        faction_info = FACTIONS.get(self.faction_name, {})
        milestones = faction_info.get("milestones", {})
        
        for milestone_rep, milestone_data in milestones.items():
            milestone_id = f"{self.faction_name}_{milestone_rep}"
            if (old_reputation < milestone_rep <= self.reputation and 
                milestone_id not in self.milestones_reached):
                self.milestones_reached.append(milestone_id)
                new_milestones.append(milestone_data["name"])
        
        # Update rank
        self.rank = self.get_rank_title()
        
        return new_milestones
    
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "character_name": self.character_name,
            "faction_name": self.faction_name,
            "reputation": self.reputation,
            "rank": self.rank,
            "last_updated": self.last_updated.isoformat(),
            "milestones_reached": self.milestones_reached,
            "faction_quests_completed": self.faction_quests_completed,
            "faction_conflicts_won": self.faction_conflicts_won
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FactionReputation':
        return cls(
            user_id=data["user_id"],
            character_name=data["character_name"],
            faction_name=data["faction_name"],
            reputation=data.get("reputation", 0),
            rank=data.get("rank", "Unknown"),
            last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat())),
            milestones_reached=data.get("milestones_reached", []),
            faction_quests_completed=data.get("faction_quests_completed", 0),
            faction_conflicts_won=data.get("faction_conflicts_won", 0)
        )

# Faction definitions and information
FACTIONS = {
    "Pirate": {
        "name": "Pirate",
        "description": "Freedom-seeking adventurers who sail the seas in search of treasure and adventure",
        "emoji": "🏴‍☠️",
        "color": 0x2c2c54,
        "opposing_factions": ["Marine", "World Government"],
        "allied_factions": ["Revolutionary"],
        "benefits": {
            "bounty_multiplier": 1.0,
            "treasure_bonus": 0.15,
            "ship_upgrade_discount": 0.1,
            "crew_size_bonus": 2
        },
        "milestones": {
            100: {"name": "Recognized Pirate", "bonus": "Small bounty poster", "unlock": ["pirate_flag_custom"]},
            300: {"name": "Notorious Pirate", "bonus": "Crew recruitment bonus", "unlock": ["feared_reputation"]},
            500: {"name": "Infamous Captain", "bonus": "Territory control", "unlock": ["pirate_alliance"]},
            750: {"name": "Legendary Pirate", "bonus": "Yonko recognition", "unlock": ["emperor_path"]},
            1000: {"name": "Pirate Emperor", "bonus": "Ultimate pirate status", "unlock": ["one_piece_quest"]}
        }
    },
    
    "Marine": {
        "name": "Marine",
        "description": "Soldiers of justice who uphold law and order across the seas",
        "emoji": "⚓",
        "color": 0x0066cc,
        "opposing_factions": ["Pirate", "Revolutionary"],
        "allied_factions": ["World Government"],
        "benefits": {
            "justice_bonus": 1.2,
            "government_support": 0.2,
            "marine_equipment_access": True,
            "backup_reinforcements": 0.15
        },
        "milestones": {
            100: {"name": "Trusted Marine", "bonus": "Equipment access", "unlock": ["marine_weapons"]},
            300: {"name": "Marine Officer", "bonus": "Command authority", "unlock": ["troop_command"]},
            500: {"name": "Marine Captain", "bonus": "Ship command", "unlock": ["warship_access"]},
            750: {"name": "Marine Commodore", "bonus": "Fleet authority", "unlock": ["justice_crusade"]},
            1000: {"name": "Marine Admiral", "bonus": "Absolute Justice", "unlock": ["world_government_access"]}
        }
    },
    
    "Revolutionary": {
        "name": "Revolutionary",
        "description": "Fighters against oppression who seek to overthrow the World Government",
        "emoji": "🔥",
        "color": 0xcc0000,
        "opposing_factions": ["Marine", "World Government"],
        "allied_factions": ["Pirate"],
        "benefits": {
            "stealth_bonus": 0.25,
            "information_network": 0.3,
            "rebellion_support": 0.2,
            "government_resistance": 0.15
        },
        "milestones": {
            100: {"name": "Revolutionary Recruit", "bonus": "Network access", "unlock": ["secret_contacts"]},
            300: {"name": "Cell Leader", "bonus": "Mission authority", "unlock": ["sabotage_operations"]},
            500: {"name": "Revolutionary Commander", "bonus": "Regional control", "unlock": ["liberation_front"]},
            750: {"name": "Army Officer", "bonus": "Strategic command", "unlock": ["dragon_audience"]},
            1000: {"name": "Revolutionary Hero", "bonus": "World liberation", "unlock": ["government_overthrow"]}
        }
    },
    
    "World Government": {
        "name": "World Government",
        "description": "The ruling authority that governs most of the world",
        "emoji": "🌍",
        "color": 0x666666,
        "opposing_factions": ["Revolutionary", "Pirate"],
        "allied_factions": ["Marine"],
        "benefits": {
            "authority_bonus": 0.3,
            "resource_access": 0.25,
            "information_control": 0.2,
            "diplomatic_immunity": True
        },
        "milestones": {
            200: {"name": "Government Agent", "bonus": "Authority access", "unlock": ["cipher_pol"]},
            500: {"name": "World Noble Favor", "bonus": "Elite privileges", "unlock": ["celestial_dragon_protection"]},
            800: {"name": "Five Elders Contact", "bonus": "Ultimate authority", "unlock": ["world_secrets"]},
            1000: {"name": "World Ruler", "bonus": "Absolute power", "unlock": ["ancient_weapons"]}
        }
    },
    
    "Neutral": {
        "name": "Neutral",
        "description": "Independent individuals who don't align with major factions",
        "emoji": "⚖️",
        "color": 0x999999,
        "opposing_factions": [],
        "allied_factions": [],
        "benefits": {
            "diplomatic_bonus": 0.2,
            "trade_bonus": 0.15,
            "faction_flexibility": True,
            "peaceful_resolution": 0.25
        },
        "milestones": {
            150: {"name": "Respected Individual", "bonus": "Diplomatic immunity", "unlock": ["neutral_territory"]},
            350: {"name": "Influential Mediator", "bonus": "Faction mediation", "unlock": ["peace_negotiations"]},
            600: {"name": "World Diplomat", "bonus": "Global influence", "unlock": ["international_authority"]},
            1000: {"name": "Peacekeeper", "bonus": "Ultimate neutrality", "unlock": ["world_peace_path"]}
        }
    },
    
    # Location-based factions
    "Village": {
        "name": "Village",
        "description": "Local villagers and townspeople across various islands",
        "emoji": "🏘️",
        "color": 0x8fbc8f,
        "benefits": {
            "local_support": 0.3,
            "safe_harbor": True,
            "supply_discount": 0.2,
            "information_network": 0.15
        }
    },
    
    "Fish-Man": {
        "name": "Fish-Man",
        "description": "The underwater kingdom and Fish-Man communities",
        "emoji": "🐟",
        "color": 0x4169e1,
        "benefits": {
            "underwater_bonus": 0.4,
            "fish_man_karate": 0.25,
            "ocean_navigation": 0.3,
            "sea_creature_alliance": True
        }
    },
    
    "Mink": {
        "name": "Mink",
        "description": "The warrior tribe from the moving island of Zou",
        "emoji": "⚡",
        "color": 0xffd700,
        "benefits": {
            "electro_mastery": 0.3,
            "loyalty_bonus": 0.25,
            "warrior_training": 0.2,
            "sulong_enhancement": 0.5
        }
    }
}

# Faction rank systems
FACTION_RANKS = {
    "Pirate": {
        -1000: {"title": "Scurvy Dog", "description": "Despised by all pirates"},
        -500: {"title": "Traitor", "description": "Betrayer of pirate code"},
        -200: {"title": "Landlubber", "description": "Not trusted by pirates"},
        0: {"title": "Unknown", "description": "No reputation among pirates"},
        50: {"title": "Rookie Pirate", "description": "New to the pirate life"},
        150: {"title": "Seasoned Pirate", "description": "Experienced seafarer"},
        300: {"title": "Notorious Pirate", "description": "Known across the seas"},
        500: {"title": "Infamous Captain", "description": "Commands respect and fear"},
        750: {"title": "Legendary Pirate", "description": "Stories told of your deeds"},
        1000: {"title": "Pirate Emperor", "description": "One of the rulers of the seas"}
    },
    
    "Marine": {
        -1000: {"title": "Traitor to Justice", "description": "Enemy of all Marines"},
        -500: {"title": "Deserter", "description": "Abandoned duty and honor"},
        -200: {"title": "Disgraced", "description": "Fallen from Marine grace"},
        0: {"title": "Civilian", "description": "No standing with Marines"},
        50: {"title": "Seaman Recruit", "description": "Lowest Marine rank"},
        150: {"title": "Petty Officer", "description": "Junior Marine officer"},
        300: {"title": "Lieutenant", "description": "Commissioned Marine officer"},
        500: {"title": "Captain", "description": "Ship and base commander"},
        750: {"title": "Commodore", "description": "Fleet commander"},
        1000: {"title": "Admiral", "description": "Highest Marine authority"}
    },
    
    "Revolutionary": {
        -1000: {"title": "Government Spy", "description": "Traitor to the revolution"},
        -500: {"title": "Oppressor", "description": "Supporter of tyranny"},
        -200: {"title": "Indifferent", "description": "Ignores injustice"},
        0: {"title": "Bystander", "description": "No revolutionary standing"},
        50: {"title": "Sympathizer", "description": "Supports the cause quietly"},
        150: {"title": "Revolutionary", "description": "Active member of the army"},
        300: {"title": "Cell Leader", "description": "Commands local operations"},
        500: {"title": "Commander", "description": "Regional revolutionary leader"},
        750: {"title": "Army Officer", "description": "High-ranking revolutionary"},
        1000: {"title": "Revolutionary Hero", "description": "Symbol of freedom"}
    }
}

def get_faction_relationships() -> Dict[str, Dict[str, float]]:
    """Get faction relationship modifiers"""
    relationships = {}
    
    for faction_name, faction_data in FACTIONS.items():
        relationships[faction_name] = {}
        
        # Set base relationships
        for other_faction in FACTIONS.keys():
            if other_faction == faction_name:
                relationships[faction_name][other_faction] = 1.0  # Self
            elif other_faction in faction_data.get("allied_factions", []):
                relationships[faction_name][other_faction] = 0.5  # Allies
            elif other_faction in faction_data.get("opposing_factions", []):
                relationships[faction_name][other_faction] = -0.5  # Enemies
            else:
                relationships[faction_name][other_faction] = 0.0  # Neutral
    
    return relationships

def calculate_reputation_change(action_faction: str, target_faction: str, base_change: int) -> Dict[str, int]:
    """Calculate reputation changes across all factions based on an action"""
    relationships = get_faction_relationships()
    changes = {}
    
    # Direct change to target faction
    changes[target_faction] = base_change
    
    # Calculate spillover effects
    if action_faction in relationships:
        for faction, relationship in relationships[action_faction].items():
            if faction != target_faction and faction != action_faction:
                spillover = int(base_change * relationship * 0.3)  # 30% spillover
                if spillover != 0:
                    changes[faction] = spillover
    
    return changes

def get_faction_benefits(faction_reputation: Dict[str, int]) -> Dict[str, float]:
    """Calculate cumulative faction benefits based on reputation"""
    total_benefits = {}
    
    for faction_name, reputation in faction_reputation.items():
        if reputation <= 0:
            continue
        
        faction_data = FACTIONS.get(faction_name, {})
        benefits = faction_data.get("benefits", {})
        
        # Scale benefits based on reputation
        reputation_multiplier = min(reputation / 500, 2.0)  # Cap at 2x benefits
        
        for benefit_name, benefit_value in benefits.items():
            if isinstance(benefit_value, (int, float)):
                current_value = total_benefits.get(benefit_name, 0.0)
                total_benefits[benefit_name] = current_value + (benefit_value * reputation_multiplier)
            else:
                total_benefits[benefit_name] = benefit_value
    
    return total_benefits