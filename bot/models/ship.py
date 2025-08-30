"""
Ship system models and mechanics
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import uuid

@dataclass
class ShipUpgrade:
    """Represents a ship upgrade or modification"""
    upgrade_id: str
    name: str
    description: str
    upgrade_type: str  # hull, sails, weapons, special
    stats_bonus: Dict[str, int] = field(default_factory=dict)
    cost: int = 0
    requirements: List[str] = field(default_factory=list)

@dataclass
class Ship:
    """Represents a crew's ship"""
    ship_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    ship_type: str = "Dinghy"  # Dinghy, Caravel, Brigantine, Galleon, Legendary
    description: str = ""
    
    # Ship stats
    durability: int = 100  # Ship HP
    max_durability: int = 100
    speed: int = 10  # Travel speed
    cargo_capacity: int = 50  # Storage space
    crew_capacity: int = 5  # Max crew size
    firepower: int = 0  # Combat strength
    
    # Ship features and upgrades
    upgrades: List[str] = field(default_factory=list)  # List of upgrade IDs
    special_features: List[str] = field(default_factory=list)
    
    # Ship customization
    figurehead: str = ""
    sail_color: str = "White"
    jolly_roger: str = "🏴‍☠️"
    
    # Ship inventory and resources
    cargo: Dict[str, int] = field(default_factory=dict)
    cannons: int = 0
    ammunition: int = 0
    
    # Ship history and status
    created_at: datetime = field(default_factory=datetime.now)
    last_repaired: datetime = field(default_factory=datetime.now)
    battles_won: int = 0
    battles_lost: int = 0
    distance_traveled: int = 0
    
    def repair(self, amount: int = None) -> int:
        """Repair the ship. Returns actual amount repaired."""
        if amount is None:
            amount = self.max_durability - self.durability
        
        actual_repair = min(amount, self.max_durability - self.durability)
        self.durability += actual_repair
        self.last_repaired = datetime.now()
        return actual_repair
    
    def take_damage(self, damage: int) -> bool:
        """Apply damage to ship. Returns True if ship is destroyed."""
        self.durability = max(0, self.durability - damage)
        return self.durability <= 0
    
    def add_cargo(self, item: str, quantity: int) -> bool:
        """Add cargo to ship. Returns True if successful."""
        current_cargo = sum(self.cargo.values())
        if current_cargo + quantity > self.cargo_capacity:
            return False
        
        self.cargo[item] = self.cargo.get(item, 0) + quantity
        return True
    
    def remove_cargo(self, item: str, quantity: int) -> bool:
        """Remove cargo from ship. Returns True if successful."""
        if self.cargo.get(item, 0) < quantity:
            return False
        
        self.cargo[item] -= quantity
        if self.cargo[item] <= 0:
            del self.cargo[item]
        return True
    
    def get_total_stats(self) -> Dict[str, int]:
        """Get ship stats including upgrades"""
        stats = {
            "durability": self.max_durability,
            "speed": self.speed,
            "cargo_capacity": self.cargo_capacity,
            "crew_capacity": self.crew_capacity,
            "firepower": self.firepower
        }
        
        # Apply upgrade bonuses
        for upgrade_id in self.upgrades:
            upgrade = SHIP_UPGRADES.get(upgrade_id)
            if upgrade:
                for stat, bonus in upgrade.stats_bonus.items():
                    stats[stat] = stats.get(stat, 0) + bonus
        
        return stats
    
    def can_upgrade(self, upgrade_id: str, crew_level: int = 1) -> bool:
        """Check if ship can be upgraded with specific upgrade"""
        if upgrade_id in self.upgrades:
            return False
        
        upgrade = SHIP_UPGRADES.get(upgrade_id)
        if not upgrade:
            return False
        
        # Check requirements
        for requirement in upgrade.requirements:
            if requirement.startswith("crew_level:"):
                required_level = int(requirement.split(":")[1])
                if crew_level < required_level:
                    return False
            elif requirement.startswith("ship_type:"):
                required_type = requirement.split(":")[1]
                if self.ship_type != required_type:
                    return False
            elif requirement.startswith("upgrade:"):
                required_upgrade = requirement.split(":")[1]
                if required_upgrade not in self.upgrades:
                    return False
        
        return True
    
    def add_upgrade(self, upgrade_id: str):
        """Add an upgrade to the ship"""
        if upgrade_id not in self.upgrades:
            self.upgrades.append(upgrade_id)
            
            # Apply permanent stat changes
            upgrade = SHIP_UPGRADES.get(upgrade_id)
            if upgrade:
                for stat, bonus in upgrade.stats_bonus.items():
                    if stat == "max_durability":
                        self.max_durability += bonus
                        self.durability += bonus  # Also heal when upgrading
                    elif stat == "speed":
                        self.speed += bonus
                    elif stat == "cargo_capacity":
                        self.cargo_capacity += bonus
                    elif stat == "crew_capacity":
                        self.crew_capacity += bonus
                    elif stat == "firepower":
                        self.firepower += bonus
    
    def upgrade_to_type(self, new_type: str):
        """Upgrade ship to a new type"""
        if new_type in SHIP_TYPES:
            type_stats = SHIP_TYPES[new_type]
            self.ship_type = new_type
            self.max_durability = type_stats["base_durability"]
            self.durability = self.max_durability
            self.speed = type_stats["base_speed"]
            self.cargo_capacity = type_stats["base_cargo"]
            self.crew_capacity = type_stats["base_crew"]
            self.firepower = type_stats["base_firepower"]
    
    def to_dict(self) -> dict:
        """Convert ship to dictionary for JSON serialization"""
        return {
            "ship_id": self.ship_id,
            "name": self.name,
            "ship_type": self.ship_type,
            "description": self.description,
            "durability": self.durability,
            "max_durability": self.max_durability,
            "speed": self.speed,
            "cargo_capacity": self.cargo_capacity,
            "crew_capacity": self.crew_capacity,
            "firepower": self.firepower,
            "upgrades": self.upgrades,
            "special_features": self.special_features,
            "figurehead": self.figurehead,
            "sail_color": self.sail_color,
            "jolly_roger": self.jolly_roger,
            "cargo": self.cargo,
            "cannons": self.cannons,
            "ammunition": self.ammunition,
            "created_at": self.created_at.isoformat(),
            "last_repaired": self.last_repaired.isoformat(),
            "battles_won": self.battles_won,
            "battles_lost": self.battles_lost,
            "distance_traveled": self.distance_traveled
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Ship':
        """Create ship from dictionary"""
        return cls(
            ship_id=data.get("ship_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            ship_type=data.get("ship_type", "Dinghy"),
            description=data.get("description", ""),
            durability=data.get("durability", 100),
            max_durability=data.get("max_durability", 100),
            speed=data.get("speed", 10),
            cargo_capacity=data.get("cargo_capacity", 50),
            crew_capacity=data.get("crew_capacity", 5),
            firepower=data.get("firepower", 0),
            upgrades=data.get("upgrades", []),
            special_features=data.get("special_features", []),
            figurehead=data.get("figurehead", ""),
            sail_color=data.get("sail_color", "White"),
            jolly_roger=data.get("jolly_roger", "🏴‍☠️"),
            cargo=data.get("cargo", {}),
            cannons=data.get("cannons", 0),
            ammunition=data.get("ammunition", 0),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            last_repaired=datetime.fromisoformat(data.get("last_repaired", datetime.now().isoformat())),
            battles_won=data.get("battles_won", 0),
            battles_lost=data.get("battles_lost", 0),
            distance_traveled=data.get("distance_traveled", 0)
        )

# Ship type definitions
SHIP_TYPES = {
    "Dinghy": {
        "emoji": "🛶",
        "description": "Small rowboat for 1-2 people",
        "base_durability": 50,
        "base_speed": 5,
        "base_cargo": 25,
        "base_crew": 2,
        "base_firepower": 0,
        "upgrade_cost": 0
    },
    "Caravel": {
        "emoji": "⛵",
        "description": "Small sailing ship for early crews",
        "base_durability": 150,
        "base_speed": 15,
        "base_cargo": 100,
        "base_crew": 5,
        "base_firepower": 1,
        "upgrade_cost": 50000
    },
    "Brigantine": {
        "emoji": "🚢",
        "description": "Medium warship with good balance",
        "base_durability": 300,
        "base_speed": 20,
        "base_cargo": 200,
        "base_crew": 10,
        "base_firepower": 3,
        "upgrade_cost": 200000
    },
    "Galleon": {
        "emoji": "🛳️",
        "description": "Large vessel for major crews",
        "base_durability": 500,
        "base_speed": 25,
        "base_cargo": 400,
        "base_crew": 15,
        "base_firepower": 5,
        "upgrade_cost": 500000
    },
    "Legendary": {
        "emoji": "👑",
        "description": "Unique ships with special abilities",
        "base_durability": 800,
        "base_speed": 35,
        "base_cargo": 600,
        "base_crew": 20,
        "base_firepower": 8,
        "upgrade_cost": 1000000
    }
}

# Ship upgrades and modifications
SHIP_UPGRADES = {
    "reinforced_hull": ShipUpgrade(
        upgrade_id="reinforced_hull",
        name="Reinforced Hull",
        description="Strengthens the ship's hull for better durability",
        upgrade_type="hull",
        stats_bonus={"max_durability": 50},
        cost=25000,
        requirements=[]
    ),
    "improved_sails": ShipUpgrade(
        upgrade_id="improved_sails",
        name="Improved Sails",
        description="Better sails for increased speed",
        upgrade_type="sails",
        stats_bonus={"speed": 5},
        cost=30000,
        requirements=[]
    ),
    "expanded_hold": ShipUpgrade(
        upgrade_id="expanded_hold",
        name="Expanded Cargo Hold",
        description="More storage space for treasure and supplies",
        upgrade_type="hull",
        stats_bonus={"cargo_capacity": 100},
        cost=40000,
        requirements=[]
    ),
    "cannon_battery": ShipUpgrade(
        upgrade_id="cannon_battery",
        name="Cannon Battery",
        description="Adds cannons for ship combat",
        upgrade_type="weapons",
        stats_bonus={"firepower": 2},
        cost=75000,
        requirements=["ship_type:Caravel"]
    ),
    "crows_nest": ShipUpgrade(
        upgrade_id="crows_nest",
        name="Crow's Nest",
        description="Improved navigation and spotting ability",
        upgrade_type="special",
        stats_bonus={"speed": 3},
        cost=20000,
        requirements=[]
    ),
    "armored_prow": ShipUpgrade(
        upgrade_id="armored_prow",
        name="Armored Prow",
        description="Reinforced front for ramming attacks",
        upgrade_type="hull",
        stats_bonus={"firepower": 1, "max_durability": 25},
        cost=60000,
        requirements=["reinforced_hull"]
    ),
    "storm_sails": ShipUpgrade(
        upgrade_id="storm_sails",
        name="Storm Sails",
        description="Special sails that work in any weather",
        upgrade_type="sails",
        stats_bonus={"speed": 8},
        cost=100000,
        requirements=["improved_sails", "crew_level:5"]
    ),
    "sea_fortress_deck": ShipUpgrade(
        upgrade_id="sea_fortress_deck",
        name="Sea Fortress Deck",
        description="Multiple cannon emplacements for maximum firepower",
        upgrade_type="weapons",
        stats_bonus={"firepower": 5},
        cost=300000,
        requirements=["cannon_battery", "ship_type:Galleon"]
    )
}

def get_ship_upgrade_tree() -> Dict[str, List[str]]:
    """Get the upgrade dependency tree"""
    tree = {}
    for upgrade_id, upgrade in SHIP_UPGRADES.items():
        tree[upgrade_id] = [req.split(":")[1] for req in upgrade.requirements if req.startswith("upgrade:")]
    return tree

def calculate_upgrade_cost(ship: Ship, upgrade_id: str) -> int:
    """Calculate the cost of an upgrade including any modifiers"""
    upgrade = SHIP_UPGRADES.get(upgrade_id)
    if not upgrade:
        return 0
    
    base_cost = upgrade.cost
    
    # Ship type modifier
    ship_modifiers = {
        "Dinghy": 0.5,
        "Caravel": 1.0,
        "Brigantine": 1.2,
        "Galleon": 1.5,
        "Legendary": 2.0
    }
    
    modifier = ship_modifiers.get(ship.ship_type, 1.0)
    return int(base_cost * modifier)