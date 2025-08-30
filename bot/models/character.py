"""
Character data model
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any
import json

@dataclass
class Character:
    """Represents a player character in the One Piece RPG"""
    
    user_id: str
    name: str
    race: str
    origin: str
    dream: str
    level: int = 1
    experience: int = 0
    bounty: int = 0
    stats: Dict[str, int] = field(default_factory=lambda: {
        "strength": 10,
        "agility": 10,
        "durability": 10,
        "intelligence": 10
    })
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    
    # Additional character data
    faction: str = ""
    ship_name: str = ""
    crew_id: str = ""
    devil_fruit: str = ""
    
    # Progress tracking
    quests_completed: list = field(default_factory=list)
    achievements: list = field(default_factory=list)
    inventory: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set faction based on origin if not already set"""
        if not self.faction:
            from .origins import ORIGINS
            if self.origin in ORIGINS:
                self.faction = ORIGINS[self.origin]["faction"]
    
    def get_total_stats(self) -> Dict[str, int]:
        """Get total stats including racial bonuses"""
        from .races import RACES
        
        race_info = RACES.get(self.race, {})
        race_bonuses = race_info.get("stats", {})
        
        total_stats = {}
        for stat_name, base_value in self.stats.items():
            bonus = race_bonuses.get(stat_name, 0)
            total_stats[stat_name] = base_value + bonus
        
        return total_stats
    
    def get_xp_for_next_level(self) -> int:
        """Calculate XP needed for next level"""
        return (self.level * 100) + (self.level * 50)  # Scaling XP requirement
    
    def add_experience(self, xp: int) -> bool:
        """Add experience and check for level up"""
        from .races import RACES
        
        # Apply human XP bonus
        if self.race == "Human":
            xp = int(xp * 1.1)  # +10% XP for humans
        
        self.experience += xp
        
        # Check for level up
        leveled_up = False
        while self.experience >= self.get_xp_for_next_level():
            self.experience -= self.get_xp_for_next_level()
            self.level += 1
            leveled_up = True
            
            # Increase base stats on level up
            for stat in self.stats:
                self.stats[stat] += 2
        
        self.last_active = datetime.now()
        return leveled_up
    
    def add_bounty(self, amount: int):
        """Add to character's bounty"""
        self.bounty = max(0, self.bounty + amount)
        self.last_active = datetime.now()
    
    def add_item(self, item_name: str, quantity: int = 1):
        """Add item to inventory"""
        if item_name in self.inventory:
            self.inventory[item_name] += quantity
        else:
            self.inventory[item_name] = quantity
    
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """Remove item from inventory. Returns True if successful."""
        if item_name not in self.inventory or self.inventory[item_name] < quantity:
            return False
        
        self.inventory[item_name] -= quantity
        if self.inventory[item_name] <= 0:
            del self.inventory[item_name]
        
        return True
    
    def has_item(self, item_name: str, quantity: int = 1) -> bool:
        """Check if character has item in required quantity"""
        return self.inventory.get(item_name, 0) >= quantity
    
    def complete_quest(self, quest_id: str, xp_reward: int = 0, bounty_reward: int = 0):
        """Mark quest as completed and give rewards"""
        if quest_id not in self.quests_completed:
            self.quests_completed.append(quest_id)
            
            if xp_reward > 0:
                self.add_experience(xp_reward)
            
            if bounty_reward > 0:
                self.add_bounty(bounty_reward)
    
    def add_achievement(self, achievement_id: str):
        """Add achievement to character"""
        if achievement_id not in self.achievements:
            self.achievements.append(achievement_id)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary for JSON serialization"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "race": self.race,
            "origin": self.origin,
            "dream": self.dream,
            "level": self.level,
            "experience": self.experience,
            "bounty": self.bounty,
            "stats": self.stats,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "faction": self.faction,
            "ship_name": self.ship_name,
            "crew_id": self.crew_id,
            "devil_fruit": self.devil_fruit,
            "quests_completed": self.quests_completed,
            "achievements": self.achievements,
            "inventory": self.inventory
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """Create character from dictionary"""
        # Parse datetime fields
        created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        last_active = datetime.fromisoformat(data.get("last_active", datetime.now().isoformat()))
        
        return cls(
            user_id=data["user_id"],
            name=data["name"],
            race=data["race"],
            origin=data["origin"],
            dream=data["dream"],
            level=data.get("level", 1),
            experience=data.get("experience", 0),
            bounty=data.get("bounty", 0),
            stats=data.get("stats", {
                "strength": 10,
                "agility": 10,
                "durability": 10,
                "intelligence": 10
            }),
            created_at=created_at,
            last_active=last_active,
            faction=data.get("faction", ""),
            ship_name=data.get("ship_name", ""),
            crew_id=data.get("crew_id", ""),
            devil_fruit=data.get("devil_fruit", ""),
            quests_completed=data.get("quests_completed", []),
            achievements=data.get("achievements", []),
            inventory=data.get("inventory", {})
        )
