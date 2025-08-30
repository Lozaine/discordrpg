"""
Crew system models and functionality
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import uuid

@dataclass
class CrewMember:
    """Represents a crew member"""
    user_id: str
    character_name: str
    role: str = "Member"  # Captain, First Mate, Navigator, Cook, Doctor, Shipwright, Musician, Fighter
    joined_at: datetime = field(default_factory=datetime.now)
    contribution_points: int = 0
    
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "character_name": self.character_name,
            "role": self.role,
            "joined_at": self.joined_at.isoformat(),
            "contribution_points": self.contribution_points
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CrewMember':
        return cls(
            user_id=data["user_id"],
            character_name=data["character_name"],
            role=data.get("role", "Member"),
            joined_at=datetime.fromisoformat(data.get("joined_at", datetime.now().isoformat())),
            contribution_points=data.get("contribution_points", 0)
        )

@dataclass
class Crew:
    """Represents a pirate crew, marine unit, or revolutionary cell"""
    crew_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    flag_emoji: str = "🏴‍☠️"
    motto: str = ""
    faction: str = "Pirate"  # Pirate, Marine, Revolutionary, Neutral
    captain_id: str = ""
    members: List[CrewMember] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    # Crew stats and progression
    total_bounty: int = 0
    reputation: int = 0
    level: int = 1
    experience: int = 0
    
    # Ship information (will link to ship system)
    ship_id: str = ""
    
    # Crew achievements and completed quests
    achievements: List[str] = field(default_factory=list)
    completed_quests: List[str] = field(default_factory=list)
    
    # Crew resources
    treasury: int = 0  # Berry (One Piece currency)
    supplies: Dict[str, int] = field(default_factory=dict)
    
    def add_member(self, user_id: str, character_name: str, role: str = "Member") -> bool:
        """Add a new member to the crew"""
        if len(self.members) >= self.get_max_members():
            return False
        
        # Check if user is already a member
        if any(member.user_id == user_id for member in self.members):
            return False
        
        member = CrewMember(user_id=user_id, character_name=character_name, role=role)
        self.members.append(member)
        return True
    
    def remove_member(self, user_id: str) -> bool:
        """Remove a member from the crew"""
        for i, member in enumerate(self.members):
            if member.user_id == user_id:
                del self.members[i]
                return True
        return False
    
    def get_member(self, user_id: str) -> Optional[CrewMember]:
        """Get a specific crew member"""
        for member in self.members:
            if member.user_id == user_id:
                return member
        return None
    
    def get_captain(self) -> Optional[CrewMember]:
        """Get the crew captain"""
        for member in self.members:
            if member.role == "Captain":
                return member
        return None
    
    def change_member_role(self, user_id: str, new_role: str) -> bool:
        """Change a member's role"""
        member = self.get_member(user_id)
        if member:
            member.role = new_role
            return True
        return False
    
    def get_max_members(self) -> int:
        """Get maximum crew size based on level"""
        base_size = 5
        level_bonus = (self.level - 1) * 2
        return min(base_size + level_bonus, 15)  # Max 15 members
    
    def add_experience(self, xp: int):
        """Add experience to crew and check for level up"""
        self.experience += xp
        
        while self.experience >= self.get_xp_for_next_level():
            self.experience -= self.get_xp_for_next_level()
            self.level += 1
    
    def get_xp_for_next_level(self) -> int:
        """Calculate XP needed for next crew level"""
        return (self.level * 200) + (self.level * 100)
    
    def add_bounty(self, amount: int):
        """Add to total crew bounty"""
        self.total_bounty += amount
        self.reputation += amount // 1000  # Reputation based on bounty
    
    def add_treasury(self, amount: int):
        """Add money to crew treasury"""
        self.treasury += amount
    
    def get_crew_bonuses(self) -> Dict[str, float]:
        """Get crew bonuses based on member roles"""
        bonuses = {
            "combat": 1.0,
            "navigation": 1.0,
            "cooking": 1.0,
            "healing": 1.0,
            "crafting": 1.0,
            "morale": 1.0
        }
        
        for member in self.members:
            if member.role == "Captain":
                bonuses["morale"] += 0.1
            elif member.role == "Navigator":
                bonuses["navigation"] += 0.15
            elif member.role == "Cook":
                bonuses["cooking"] += 0.2
            elif member.role == "Doctor":
                bonuses["healing"] += 0.25
            elif member.role == "Shipwright":
                bonuses["crafting"] += 0.15
            elif member.role == "Musician":
                bonuses["morale"] += 0.15
            elif member.role == "Fighter":
                bonuses["combat"] += 0.1
        
        return bonuses
    
    def to_dict(self) -> dict:
        """Convert crew to dictionary for JSON serialization"""
        return {
            "crew_id": self.crew_id,
            "name": self.name,
            "description": self.description,
            "flag_emoji": self.flag_emoji,
            "motto": self.motto,
            "faction": self.faction,
            "captain_id": self.captain_id,
            "members": [member.to_dict() for member in self.members],
            "created_at": self.created_at.isoformat(),
            "total_bounty": self.total_bounty,
            "reputation": self.reputation,
            "level": self.level,
            "experience": self.experience,
            "ship_id": self.ship_id,
            "achievements": self.achievements,
            "completed_quests": self.completed_quests,
            "treasury": self.treasury,
            "supplies": self.supplies
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Crew':
        """Create crew from dictionary"""
        members = [CrewMember.from_dict(member_data) for member_data in data.get("members", [])]
        
        return cls(
            crew_id=data.get("crew_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            flag_emoji=data.get("flag_emoji", "🏴‍☠️"),
            motto=data.get("motto", ""),
            faction=data.get("faction", "Pirate"),
            captain_id=data.get("captain_id", ""),
            members=members,
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            total_bounty=data.get("total_bounty", 0),
            reputation=data.get("reputation", 0),
            level=data.get("level", 1),
            experience=data.get("experience", 0),
            ship_id=data.get("ship_id", ""),
            achievements=data.get("achievements", []),
            completed_quests=data.get("completed_quests", []),
            treasury=data.get("treasury", 0),
            supplies=data.get("supplies", {})
        )

# Crew role definitions and bonuses
CREW_ROLES = {
    "Captain": {
        "emoji": "👑",
        "description": "Leader of the crew, decides direction and gives morale bonus",
        "limit": 1,
        "bonuses": {"morale": 0.1, "leadership": 0.2}
    },
    "First Mate": {
        "emoji": "⚓",
        "description": "Second in command, assists captain with leadership",
        "limit": 1,
        "bonuses": {"morale": 0.05, "leadership": 0.1}
    },
    "Navigator": {
        "emoji": "🧭",
        "description": "Charts the course and reduces travel time",
        "limit": 2,
        "bonuses": {"navigation": 0.15, "weather_prediction": 0.1}
    },
    "Cook": {
        "emoji": "👨‍🍳",
        "description": "Provides food buffs and heals crew after battles",
        "limit": 2,
        "bonuses": {"cooking": 0.2, "healing": 0.1}
    },
    "Doctor": {
        "emoji": "⚕️",
        "description": "Heals crew members and reduces death penalties",
        "limit": 2,
        "bonuses": {"healing": 0.25, "medicine": 0.2}
    },
    "Shipwright": {
        "emoji": "🔨",
        "description": "Repairs and upgrades the ship",
        "limit": 2,
        "bonuses": {"crafting": 0.15, "ship_repair": 0.2}
    },
    "Musician": {
        "emoji": "🎵",
        "description": "Boosts crew morale and provides unique buffs",
        "limit": 2,
        "bonuses": {"morale": 0.15, "inspiration": 0.1}
    },
    "Fighter": {
        "emoji": "⚔️",
        "description": "General combat specialist",
        "limit": 99,
        "bonuses": {"combat": 0.1}
    }
}

def get_available_roles(crew: Crew) -> List[str]:
    """Get list of available roles for a crew"""
    available = []
    role_counts = {}
    
    # Count current roles
    for member in crew.members:
        role_counts[member.role] = role_counts.get(member.role, 0) + 1
    
    # Check which roles are available
    for role, info in CREW_ROLES.items():
        current_count = role_counts.get(role, 0)
        if current_count < info["limit"]:
            available.append(role)
    
    return available