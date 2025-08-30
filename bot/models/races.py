"""
Character races data and definitions
"""

RACES = {
    "Human": {
        "emoji": "👤",
        "stats": {
            "strength": 1,
            "agility": 1,
            "durability": 1,
            "intelligence": 1
        },
        "ability": "Adaptability: +10% more EXP from all sources",
        "description": "The adaptable majority of the world, humans excel through versatility and determination.",
        "extra": "Flexible storylines, can join any faction without penalties"
    },
    
    "Fish-Man": {
        "emoji": "🐟",
        "stats": {
            "strength": 2,
            "durability": 1
        },
        "ability": "Water Breathing: No underwater penalties, can use Fish-Man Karate",
        "description": "Lords of the sea with incredible underwater abilities and natural strength.",
        "extra": "Easier access to rare underwater quests & treasures"
    },
    
    "Mink": {
        "emoji": "⚡",
        "stats": {
            "agility": 2,
            "strength": 1
        },
        "ability": "Electro: Basic lightning attacks with stun chance. Sulong form during full moon events",
        "description": "Lightning furies from Zou with natural electrical abilities and warrior instincts.",
        "extra": "Unique quests tied to Zou and the Mink Tribe's honor code"
    },
    
    "Skypiean": {
        "emoji": "☁️",
        "stats": {
            "intelligence": 2,
            "agility": 1
        },
        "ability": "Sky-Dweller: Reduced fall damage, starts with a Dial (Impact/Wind)",
        "description": "Children of the clouds with advanced technology and aerial superiority.",
        "extra": "Easier navigation to Sky Islands and Dial-based crafting system"
    },
    
    "Giant": {
        "emoji": "🗿",
        "stats": {
            "strength": 4,
            "durability": 2,
            "agility": -2
        },
        "ability": "Giant's Strength: Wield oversized weapons, resistant to knockback",
        "description": "Titans of the seas with incredible physical power but limited mobility.",
        "extra": "Giants can't stealth or hide, but can crush groups in combat"
    }
}

# Special unlockable race (for future implementation)
SPECIAL_RACES = {
    "Cyborg": {
        "emoji": "🤖",
        "stats": {
            "durability": 3,
            "strength": 2
        },
        "ability": "Mechanical Upgrade: Access to custom modules (rocket boosters, laser cannons)",
        "description": "Enhanced beings with mechanical parts and technological advantages.",
        "extra": "Repair system instead of natural healing",
        "unlock_requirement": "Complete Franky storyline quest"
    }
}

def get_race_abilities(race_name: str) -> dict:
    """Get specific abilities for a race"""
    race_abilities = {
        "Human": {
            "adaptability": {"type": "passive", "effect": "xp_multiplier", "value": 1.1}
        },
        "Fish-Man": {
            "water_breathing": {"type": "passive", "effect": "underwater_immunity"},
            "fishman_karate": {"type": "command", "command": "/fishman_karate", "cooldown": 300}
        },
        "Mink": {
            "electro": {"type": "active", "damage": "1d6+agility", "stun_chance": 0.15},
            "sulong": {"type": "event", "trigger": "full_moon", "multiplier": 2.0}
        },
        "Skypiean": {
            "sky_dweller": {"type": "passive", "effect": "fall_damage_reduction", "value": 0.5},
            "dial_mastery": {"type": "passive", "effect": "dial_crafting_bonus"}
        },
        "Giant": {
            "giants_strength": {"type": "passive", "effect": "weapon_size_bonus"},
            "knockback_resistance": {"type": "passive", "effect": "status_resistance", "value": 0.3}
        }
    }
    
    return race_abilities.get(race_name, {})

def get_racial_stat_bonus(race_name: str) -> dict:
    """Get stat bonuses for a race"""
    race_data = RACES.get(race_name)
    if race_data:
        return race_data.get("stats", {})
    return {}

def is_race_available(race_name: str, user_unlocks: list = []) -> bool:
    """Check if a race is available to a user"""
    if race_name in RACES:
        return True
    
    if race_name in SPECIAL_RACES:
        if user_unlocks is None:
            return False
        
        unlock_requirement = SPECIAL_RACES[race_name].get("unlock_requirement", "")
        return unlock_requirement in user_unlocks
    
    return False
