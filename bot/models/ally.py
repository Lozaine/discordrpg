"""
Ally system for recruiting and managing canonical One Piece characters
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class AllyRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class AllyAbility:
    """Ally special ability"""
    ability_id: str
    name: str
    description: str
    ability_type: str  # passive, active, summon
    cooldown: int = 0  # In seconds
    effect: Dict[str, float] = field(default_factory=dict)

@dataclass
class Ally:
    """Canonical character that can be recruited as an ally"""
    ally_id: str
    name: str
    title: str
    description: str
    rarity: AllyRarity
    
    # Ally stats and bonuses
    level: int = 1
    max_level: int = 50
    bond_level: int = 1
    max_bond: int = 10
    
    # Passive bonuses the ally provides
    stat_bonuses: Dict[str, int] = field(default_factory=dict)
    passive_effects: Dict[str, float] = field(default_factory=dict)
    
    # Active abilities
    abilities: List[AllyAbility] = field(default_factory=list)
    
    # Recruitment requirements
    unlock_requirements: List[str] = field(default_factory=list)
    recruitment_cost: Dict[str, int] = field(default_factory=dict)
    
    # Ally progression
    experience: int = 0
    bond_points: int = 0
    
    # Visual representation
    emoji: str = "👤"
    faction: str = "Neutral"
    origin: str = ""
    
    def get_total_stat_bonus(self, stat: str) -> int:
        """Get total stat bonus including level and bond scaling"""
        base_bonus = self.stat_bonuses.get(stat, 0)
        level_multiplier = 1 + (self.level - 1) * 0.1  # 10% per level
        bond_multiplier = 1 + (self.bond_level - 1) * 0.05  # 5% per bond level
        return int(base_bonus * level_multiplier * bond_multiplier)
    
    def get_passive_effect(self, effect: str) -> float:
        """Get passive effect value including scaling"""
        base_effect = self.passive_effects.get(effect, 0.0)
        level_multiplier = 1 + (self.level - 1) * 0.02  # 2% per level
        bond_multiplier = 1 + (self.bond_level - 1) * 0.03  # 3% per bond level
        return base_effect * level_multiplier * bond_multiplier
    
    def add_experience(self, xp: int) -> bool:
        """Add experience and check for level up"""
        self.experience += xp
        leveled_up = False
        
        while self.experience >= self.get_xp_for_next_level() and self.level < self.max_level:
            self.experience -= self.get_xp_for_next_level()
            self.level += 1
            leveled_up = True
        
        return leveled_up
    
    def add_bond_points(self, points: int) -> bool:
        """Add bond points and check for bond level up"""
        self.bond_points += points
        bond_leveled = False
        
        while self.bond_points >= self.get_bond_for_next_level() and self.bond_level < self.max_bond:
            self.bond_points -= self.get_bond_for_next_level()
            self.bond_level += 1
            bond_leveled = True
        
        return bond_leveled
    
    def get_xp_for_next_level(self) -> int:
        """Calculate XP needed for next level"""
        return (self.level * 100) + (self.level * 25)
    
    def get_bond_for_next_level(self) -> int:
        """Calculate bond points needed for next bond level"""
        return (self.bond_level * 50) + (self.bond_level * 20)
    
    def to_dict(self) -> dict:
        return {
            "ally_id": self.ally_id,
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "rarity": self.rarity.value,
            "level": self.level,
            "max_level": self.max_level,
            "bond_level": self.bond_level,
            "max_bond": self.max_bond,
            "stat_bonuses": self.stat_bonuses,
            "passive_effects": self.passive_effects,
            "abilities": [{"ability_id": ab.ability_id, "name": ab.name, "description": ab.description, 
                          "ability_type": ab.ability_type, "cooldown": ab.cooldown, "effect": ab.effect} 
                         for ab in self.abilities],
            "unlock_requirements": self.unlock_requirements,
            "recruitment_cost": self.recruitment_cost,
            "experience": self.experience,
            "bond_points": self.bond_points,
            "emoji": self.emoji,
            "faction": self.faction,
            "origin": self.origin
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Ally':
        abilities = []
        for ab_data in data.get("abilities", []):
            abilities.append(AllyAbility(
                ability_id=ab_data["ability_id"],
                name=ab_data["name"],
                description=ab_data["description"],
                ability_type=ab_data["ability_type"],
                cooldown=ab_data.get("cooldown", 0),
                effect=ab_data.get("effect", {})
            ))
        
        return cls(
            ally_id=data["ally_id"],
            name=data["name"],
            title=data["title"],
            description=data["description"],
            rarity=AllyRarity(data["rarity"]),
            level=data.get("level", 1),
            max_level=data.get("max_level", 50),
            bond_level=data.get("bond_level", 1),
            max_bond=data.get("max_bond", 10),
            stat_bonuses=data.get("stat_bonuses", {}),
            passive_effects=data.get("passive_effects", {}),
            abilities=abilities,
            unlock_requirements=data.get("unlock_requirements", []),
            recruitment_cost=data.get("recruitment_cost", {}),
            experience=data.get("experience", 0),
            bond_points=data.get("bond_points", 0),
            emoji=data.get("emoji", "👤"),
            faction=data.get("faction", "Neutral"),
            origin=data.get("origin", "")
        )

@dataclass
class PlayerAlly:
    """Player's recruited ally instance"""
    user_id: str
    character_name: str
    ally_id: str
    recruited_at: datetime = field(default_factory=datetime.now)
    times_used: int = 0
    last_used: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "character_name": self.character_name,
            "ally_id": self.ally_id,
            "recruited_at": self.recruited_at.isoformat(),
            "times_used": self.times_used,
            "last_used": self.last_used.isoformat() if self.last_used else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PlayerAlly':
        return cls(
            user_id=data["user_id"],
            character_name=data["character_name"],
            ally_id=data["ally_id"],
            recruited_at=datetime.fromisoformat(data["recruited_at"]),
            times_used=data.get("times_used", 0),
            last_used=datetime.fromisoformat(data["last_used"]) if data.get("last_used") else None
        )

# Canonical One Piece characters as allies
AVAILABLE_ALLIES = {
    # Early Game Allies (East Blue)
    "zoro_early": Ally(
        ally_id="zoro_early",
        name="Roronoa Zoro",
        title="The Wandering Swordsman",
        description="A skilled swordsman seeking to become the world's greatest.",
        rarity=AllyRarity.UNCOMMON,
        stat_bonuses={"strength": 5, "agility": 3},
        passive_effects={"sword_damage": 0.15, "critical_chance": 0.05},
        abilities=[
            AllyAbility("oni_giri", "Oni Giri", "Powerful three-sword technique", "active", 300, {"damage_multiplier": 2.0})
        ],
        unlock_requirements=["complete_quest:romance_dawn_marine", "location:shells_town"],
        recruitment_cost={"berry": 10000, "sake": 3},
        emoji="⚔️",
        faction="Pirate",
        origin="Shells Town"
    ),
    
    "nami_early": Ally(
        ally_id="nami_early",
        name="Nami",
        title="The Cat Burglar",
        description="A skilled navigator and thief with a talent for weather prediction.",
        rarity=AllyRarity.COMMON,
        stat_bonuses={"intelligence": 4, "agility": 2},
        passive_effects={"gold_bonus": 0.1, "navigation_speed": 0.2},
        abilities=[
            AllyAbility("weather_sense", "Weather Sense", "Predict weather patterns for safer travel", "passive", 0, {"storm_avoidance": 0.3})
        ],
        unlock_requirements=["complete_quest:syrup_village_main"],
        recruitment_cost={"berry": 15000, "navigation_tools": 1},
        emoji="🍊",
        faction="Pirate",
        origin="Cocoyasi Village"
    ),
    
    "usopp": Ally(
        ally_id="usopp",
        name="Usopp",
        title="The Brave Warrior of the Sea",
        description="A skilled marksman with a talent for invention and storytelling.",
        rarity=AllyRarity.COMMON,
        stat_bonuses={"agility": 3, "intelligence": 3},
        passive_effects={"accuracy": 0.15, "crafting_speed": 0.1},
        abilities=[
            AllyAbility("exploding_star", "Exploding Star", "Ranged explosive attack", "active", 180, {"area_damage": 1.5})
        ],
        unlock_requirements=["complete_quest:syrup_village_main", "dream:Brave Warrior of the Sea"],
        recruitment_cost={"berry": 8000, "slingshot_materials": 2},
        emoji="🎯",
        faction="Pirate",
        origin="Syrup Village"
    ),
    
    "sanji": Ally(
        ally_id="sanji",
        name="Sanji",
        title="The Black Leg Cook",
        description="A master chef who fights with powerful kicks.",
        rarity=AllyRarity.RARE,
        stat_bonuses={"strength": 4, "agility": 4, "intelligence": 2},
        passive_effects={"cooking_quality": 0.25, "kick_damage": 0.2},
        abilities=[
            AllyAbility("diable_jambe", "Diable Jambe", "Flaming kick technique", "active", 240, {"fire_damage": 2.5})
        ],
        unlock_requirements=["complete_quest:baratie_cooking_special", "dream:Find the All Blue"],
        recruitment_cost={"berry": 25000, "rare_ingredients": 5},
        emoji="👨‍🍳",
        faction="Pirate",
        origin="Baratie"
    ),
    
    # Mid-Game Allies
    "chopper": Ally(
        ally_id="chopper",
        name="Tony Tony Chopper",
        title="The Cotton Candy Lover",
        description="A reindeer doctor with multiple transformation forms.",
        rarity=AllyRarity.RARE,
        stat_bonuses={"intelligence": 5, "durability": 3},
        passive_effects={"healing_effectiveness": 0.3, "medicine_crafting": 0.25},
        abilities=[
            AllyAbility("rumble_ball", "Rumble Ball", "Transformation enhancement", "active", 600, {"all_stats": 1.5})
        ],
        unlock_requirements=["complete_quest:drum_island_main", "level:10"],
        recruitment_cost={"berry": 50000, "medical_supplies": 10},
        emoji="🦌",
        faction="Pirate",
        origin="Drum Island"
    ),
    
    # Special Event Allies
    "ace": Ally(
        ally_id="ace",
        name="Portgas D. Ace",
        title="Fire Fist Ace",
        description="Logia Devil Fruit user with incredible fire powers.",
        rarity=AllyRarity.LEGENDARY,
        stat_bonuses={"strength": 8, "agility": 6, "durability": 5},
        passive_effects={"fire_immunity": 1.0, "logia_defense": 0.4},
        abilities=[
            AllyAbility("fire_fist", "Fire Fist", "Devastating fire punch attack", "active", 450, {"fire_damage": 4.0})
        ],
        unlock_requirements=["special_event:marineford_memorial", "level:25"],
        recruitment_cost={"berry": 200000, "flame_dial": 1, "rare_vivre_card": 1},
        emoji="🔥",
        faction="Pirate",
        origin="Unknown"
    ),
    
    "sabo": Ally(
        ally_id="sabo",
        name="Sabo",
        title="Chief of Staff of the Revolutionary Army",
        description="Revolutionary Army officer with incredible combat skills.",
        rarity=AllyRarity.EPIC,
        stat_bonuses={"strength": 7, "intelligence": 6, "agility": 5},
        passive_effects={"revolutionary_missions": 0.2, "xp_bonus": 0.15},
        abilities=[
            AllyAbility("dragon_claw", "Dragon Claw", "Powerful martial arts technique", "active", 300, {"armor_break": 3.0})
        ],
        unlock_requirements=["faction:Revolutionary", "complete_quest:dressrosa_main", "level:20"],
        recruitment_cost={"berry": 150000, "revolutionary_intel": 5},
        emoji="🐉",
        faction="Revolutionary",
        origin="Goa Kingdom"
    ),
    
    # Marine Allies
    "coby": Ally(
        ally_id="coby",
        name="Coby",
        title="Marine Petty Officer",
        description="A determined young Marine with strong conviction.",
        rarity=AllyRarity.COMMON,
        stat_bonuses={"durability": 3, "intelligence": 2},
        passive_effects={"marine_reputation": 0.1, "justice_bonus": 0.05},
        abilities=[
            AllyAbility("rokushiki_basics", "Rokushiki Basics", "Basic Marine combat techniques", "passive", 0, {"combat_efficiency": 1.2})
        ],
        unlock_requirements=["faction:Marine", "complete_quest:romance_dawn_marine"],
        recruitment_cost={"berry": 5000, "marine_recommendation": 1},
        emoji="⚓",
        faction="Marine",
        origin="Shells Town"
    ),
    
    "smoker": Ally(
        ally_id="smoker",
        name="Smoker",
        title="White Hunter",
        description="Marine Captain with Smoke-Smoke Devil Fruit powers.",
        rarity=AllyRarity.EPIC,
        stat_bonuses={"strength": 6, "durability": 6, "intelligence": 4},
        passive_effects={"smoke_immunity": 1.0, "marine_authority": 0.3},
        abilities=[
            AllyAbility("white_out", "White Out", "Area smoke attack", "active", 360, {"area_disable": 2.0})
        ],
        unlock_requirements=["faction:Marine", "rank:Captain", "level:15"],
        recruitment_cost={"berry": 100000, "marine_merit": 20},
        emoji="💨",
        faction="Marine",
        origin="Loguetown"
    )
}

def get_available_allies_for_player(character, completed_quests: List[str], player_level: int) -> List[Ally]:
    """Get list of allies available for recruitment by a player"""
    available = []
    
    for ally in AVAILABLE_ALLIES.values():
        # Check level requirement
        level_req = 1
        for req in ally.unlock_requirements:
            if req.startswith("level:"):
                level_req = int(req.split(":")[1])
                break
        
        if player_level < level_req:
            continue
        
        # Check other requirements
        meets_requirements = True
        for requirement in ally.unlock_requirements:
            if requirement.startswith("complete_quest:"):
                quest_id = requirement.split(":", 1)[1]
                if quest_id not in completed_quests:
                    meets_requirements = False
                    break
            elif requirement.startswith("faction:"):
                required_faction = requirement.split(":", 1)[1]
                if character.faction != required_faction:
                    meets_requirements = False
                    break
            elif requirement.startswith("dream:"):
                required_dream = requirement.split(":", 1)[1]
                if character.dream != required_dream:
                    meets_requirements = False
                    break
            elif requirement.startswith("location:"):
                # TODO: Implement location-based requirements
                pass
            elif requirement.startswith("special_event:"):
                # TODO: Implement special event requirements
                pass
        
        if meets_requirements:
            available.append(ally)
    
    return available

def calculate_ally_recruitment_cost(ally: Ally, player_reputation: Dict[str, int]) -> Dict[str, int]:
    """Calculate actual recruitment cost including reputation discounts"""
    base_cost = ally.recruitment_cost.copy()
    
    # Apply faction reputation discounts
    if ally.faction in player_reputation:
        reputation = player_reputation[ally.faction]
        if reputation >= 500:
            discount = 0.3  # 30% discount for high reputation
        elif reputation >= 200:
            discount = 0.15  # 15% discount for good reputation
        elif reputation >= 100:
            discount = 0.05  # 5% discount for decent reputation
        else:
            discount = 0.0
        
        # Apply discount to berry cost
        if "berry" in base_cost:
            base_cost["berry"] = int(base_cost["berry"] * (1 - discount))
    
    return base_cost