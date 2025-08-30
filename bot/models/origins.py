"""
Character origin islands and their associated factions and storylines
"""

ORIGINS = {
    "Shells Town": {
        "emoji": "🏛️",
        "faction": "Marine Recruit",
        "story": "The Tyrant's Fall",
        "description": "Join the Marines under Captain Morgan, uncover corruption, and decide whether to remain a loyal soldier or desert.",
        "starting_bonus": {
            "items": ["Marine Uniform", "Standard Issue Sword"],
            "stats": {"durability": 2}
        },
        "unlock_conditions": None
    },
    
    "Syrup Village": {
        "emoji": "🏘️",
        "faction": "Pirate Hopeful",
        "story": "The Liar's Legacy",
        "description": "Inspired by Usopp's tales, defend the village from pirates while seeking a ship and crew of your own.",
        "starting_bonus": {
            "items": ["Slingshot", "Village Map"],
            "stats": {"agility": 2}
        },
        "unlock_conditions": None
    },
    
    "Ohara": {
        "emoji": "📚",
        "faction": "Revolutionary Seed",
        "story": "Whispers of Truth",
        "description": "Survivor of knowledge's destruction, drawn toward forbidden texts and the Revolutionary Army's mission.",
        "starting_bonus": {
            "items": ["Ancient Text Fragment", "Scholar's Notes"],
            "stats": {"intelligence": 3}
        },
        "unlock_conditions": None
    },
    
    "Baratie": {
        "emoji": "🍳",
        "faction": "Neutral Cook/Brawler",
        "story": "A Taste of the Grand Line",
        "description": "Train as a cook, fend off invading pirates, and discover the art of fighting while feeding allies.",
        "starting_bonus": {
            "items": ["Chef's Knife", "Cooking Recipes"],
            "stats": {"strength": 1, "intelligence": 1}
        },
        "unlock_conditions": None
    },
    
    "Loguetown": {
        "emoji": "⚰️",
        "faction": "Free Choice",
        "story": "Dreams at Dawn",
        "description": "On the island where the Pirate King died, decide if you'll follow in his footsteps, uphold justice, or burn the system down.",
        "starting_bonus": {
            "items": ["Log Pose", "Execution Platform Fragment"],
            "stats": {"strength": 1, "agility": 1}
        },
        "faction_choice": ["Pirate", "Marine", "Revolutionary"],
        "unlock_conditions": None
    },
    
    "Skypiea": {
        "emoji": "☁️",
        "faction": "Neutral Adventurer",
        "story": "The Sky's Burden",
        "description": "Explore the mysteries of the sky people while dealing with conflicts between Shandians and Skypieans.",
        "starting_bonus": {
            "items": ["Wind Dial", "Sky Island Map"],
            "stats": {"agility": 2}
        },
        "unlock_conditions": None
    }
}

# Special unlock origins (for future implementation)
SPECIAL_ORIGINS = {
    "Elbaf": {
        "emoji": "⚔️",
        "faction": "Giant Warrior's Path",
        "story": "Pride of the Warriors",
        "description": "Prove yourself in trials of honor and giant combat before leaving your homeland.",
        "starting_bonus": {
            "items": ["Giant's Weapon", "Warrior's Honor"],
            "stats": {"strength": 3, "durability": 2}
        },
        "unlock_conditions": "Must be Giant race",
        "race_requirement": "Giant"
    },
    
    "Zou": {
        "emoji": "🐘",
        "faction": "Mink Guardian",
        "story": "The Moving Island",
        "description": "Protect the ancient secrets of Zou while mastering the ways of the Mink warriors.",
        "starting_bonus": {
            "items": ["Electro Gauntlets", "Ancient Poneglyph Fragment"],
            "stats": {"agility": 3, "intelligence": 1}
        },
        "unlock_conditions": "Must be Mink race",
        "race_requirement": "Mink"
    },
    
    "Fish-Man Island": {
        "emoji": "🫧",
        "faction": "Deep Sea Warrior",
        "story": "Depths of Prejudice",
        "description": "Navigate the complex politics between Fish-Men and humans while mastering underwater combat.",
        "starting_bonus": {
            "items": ["Coral Blade", "Underwater Breathing Apparatus"],
            "stats": {"strength": 2, "durability": 2}
        },
        "unlock_conditions": "Must be Fish-Man race",
        "race_requirement": "Fish-Man"
    }
}

def get_origin_factions(origin_name: str) -> list:
    """Get available factions for an origin"""
    origin_data = ORIGINS.get(origin_name) or SPECIAL_ORIGINS.get(origin_name)
    
    if not origin_data:
        return []
    
    if "faction_choice" in origin_data:
        return origin_data["faction_choice"]
    else:
        return [origin_data["faction"]]

def get_origin_starting_bonus(origin_name: str) -> dict:
    """Get starting bonus for an origin"""
    origin_data = ORIGINS.get(origin_name) or SPECIAL_ORIGINS.get(origin_name)
    
    if origin_data and "starting_bonus" in origin_data:
        return origin_data["starting_bonus"]
    
    return {"items": [], "stats": {}}

def is_origin_available(origin_name: str, character_race: str = "") -> bool:
    """Check if an origin is available for a character"""
    # Check regular origins
    if origin_name in ORIGINS:
        return True
    
    # Check special origins
    if origin_name in SPECIAL_ORIGINS:
        origin_data = SPECIAL_ORIGINS[origin_name]
        
        # Check race requirement
        if "race_requirement" in origin_data:
            return character_race == origin_data["race_requirement"]
    
    return False

def get_origin_quests(origin_name: str) -> list:
    """Get starting quests for an origin (for future quest system)"""
    origin_quests = {
        "Shells Town": [
            "marine_training_basics",
            "captain_morgan_encounter",
            "corruption_investigation"
        ],
        "Syrup Village": [
            "usopp_tales_inspiration",
            "village_defense",
            "first_ship_quest"
        ],
        "Ohara": [
            "survivor_story",
            "forbidden_knowledge_seek",
            "revolutionary_contact"
        ],
        "Baratie": [
            "cooking_basics",
            "pirate_defense",
            "sanji_inspiration"
        ],
        "Loguetown": [
            "execution_platform_visit",
            "faction_choice_quest",
            "gol_d_roger_legacy"
        ],
        "Skypiea": [
            "sky_island_navigation",
            "shandian_conflict",
            "dial_mastery_basics"
        ]
    }
    
    return origin_quests.get(origin_name, [])
