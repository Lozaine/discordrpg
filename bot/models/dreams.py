"""
Character dreams/goals system - replaces traditional classes
"""

DREAMS = {
    "World's Greatest Swordsman": {
        "emoji": "⚔️",
        "bonus": "Start with a Katana and Swordsman skill tree",
        "unlocks": "Unique duel quests against rival sword-users",
        "description": "Follow the path of the blade and surpass all who came before you.",
        "starting_items": ["Katana", "Sword Maintenance Kit"],
        "skill_trees": ["swordsman"],
        "stat_bonus": {"strength": 2, "agility": 1},
        "special_commands": ["/duel", "/sword_stance"]
    },
    
    "Find the All Blue": {
        "emoji": "🐟",
        "bonus": "Start with cooking recipes and Cook buffs",
        "unlocks": "Craft food that restores HP, buffs allies, or grants travel bonuses",
        "description": "Seek the legendary sea where all fish from every ocean gather.",
        "starting_items": ["Chef's Knife", "Recipe Book", "Cooking Pot"],
        "skill_trees": ["cook"],
        "stat_bonus": {"intelligence": 2, "agility": 1},
        "special_commands": ["/cook", "/food_buff"]
    },
    
    "Map the World": {
        "emoji": "🗺️",
        "bonus": "Start with a Log Pose and Navigate abilities",
        "unlocks": "Hidden locations, reduced travel cooldowns, chance to find rare islands",
        "description": "Chart every island, sea, and sky route across the vast world.",
        "starting_items": ["Log Pose", "Navigation Tools", "Blank Maps"],
        "skill_trees": ["navigator"],
        "stat_bonus": {"intelligence": 3},
        "special_commands": ["/navigate", "/chart_course"]
    },
    
    "Brave Warrior of the Sea": {
        "emoji": "💪",
        "bonus": "Start with high base HP and Brawler/Marksman skills",
        "unlocks": "Tanky frontline fighter abilities and warrior trials",
        "description": "Become a legendary warrior whose bravery inspires others.",
        "starting_items": ["Warrior's Band", "Training Weights"],
        "skill_trees": ["brawler", "marksman"],
        "stat_bonus": {"strength": 2, "durability": 2},
        "special_commands": ["/warrior_cry", "/inspiring_presence"]
    },
    
    "Master Devil Fruits": {
        "emoji": "🍎",
        "bonus": "Enhanced ability to sense and find Devil Fruits",
        "unlocks": "Higher Devil Fruit discovery rate and fruit mastery system",
        "description": "Understand the mysteries of Devil Fruits and their incredible powers.",
        "starting_items": ["Devil Fruit Encyclopedia", "Fruit Detector"],
        "skill_trees": ["devil_fruit_hunter"],
        "stat_bonus": {"intelligence": 2, "durability": 1},
        "special_commands": ["/fruit_hunt", "/analyze_fruit"]
    },
    
    "Topple the World Government": {
        "emoji": "🔥",
        "bonus": "Revolutionary alignment and access to hidden propaganda quests",
        "unlocks": "Rally ability - boosts morale and XP gain for nearby allies",
        "description": "Burn down the corrupt system and build a world of true freedom.",
        "starting_items": ["Revolutionary Pamphlet", "Hidden Communicator"],
        "skill_trees": ["revolutionary"],
        "stat_bonus": {"intelligence": 2, "strength": 1},
        "special_commands": ["/rally", "/sabotage"]
    },
    
    "Become Pirate King": {
        "emoji": "👑",
        "bonus": "Balanced buffs across multiple skill trees",
        "unlocks": "Access to Raftel storyline quests and ultimate pirate challenges",
        "description": "Follow in Gol D. Roger's footsteps and claim the title of Pirate King.",
        "starting_items": ["Pirate Flag", "Captain's Hat", "Treasure Map Fragment"],
        "skill_trees": ["pirate_king", "leadership", "combat"],
        "stat_bonus": {"strength": 1, "agility": 1, "durability": 1, "intelligence": 1},
        "special_commands": ["/conqueror_haki", "/pirate_declaration"],
        "difficulty": "legendary"
    }
}

# Dream progression milestones
DREAM_MILESTONES = {
    "World's Greatest Swordsman": [
        {"level": 5, "reward": "Sword Technique: Basic Slash", "description": "Learn your first sword technique"},
        {"level": 10, "reward": "Duel Challenge Access", "description": "Can now challenge other swordsmen to duels"},
        {"level": 20, "reward": "Master's Blade", "description": "Receive a high-quality sword"},
        {"level": 35, "reward": "Legendary Swordsman Recognition", "description": "Gain reputation among sword masters"},
        {"level": 50, "reward": "Path to Mihawk", "description": "Unlock quest line to face Dracule Mihawk"}
    ],
    
    "Find the All Blue": [
        {"level": 5, "reward": "Advanced Recipes", "description": "Learn more complex cooking recipes"},
        {"level": 10, "reward": "Floating Restaurant", "description": "Gain access to sea restaurant mechanics"},
        {"level": 20, "reward": "Rare Ingredient Detector", "description": "Find rare cooking ingredients easier"},
        {"level": 35, "reward": "Master Chef Recognition", "description": "Other chefs acknowledge your skills"},
        {"level": 50, "reward": "All Blue Vision", "description": "Begin to sense the location of All Blue"}
    ],
    
    "Map the World": [
        {"level": 5, "reward": "Weather Prediction", "description": "Predict weather patterns for safer travel"},
        {"level": 10, "reward": "Secret Route Discovery", "description": "Find hidden paths between islands"},
        {"level": 20, "reward": "Master Navigator Tools", "description": "Receive professional navigation equipment"},
        {"level": 35, "reward": "World Map Contributor", "description": "Your maps become sought after by others"},
        {"level": 50, "reward": "Grand Line Master", "description": "Navigate the Grand Line without Log Poses"}
    ],
    
    "Brave Warrior of the Sea": [
        {"level": 5, "reward": "Battle Cry", "description": "Inspire allies with your warrior spirit"},
        {"level": 10, "reward": "Warrior's Endurance", "description": "Increased stamina in long battles"},
        {"level": 20, "reward": "Legendary Warrior Gear", "description": "Receive equipment worthy of a true warrior"},
        {"level": 35, "reward": "Warrior's Legend", "description": "Your reputation inspires others to fight"},
        {"level": 50, "reward": "Sea's Bravest Warrior", "description": "Recognized as one of the world's greatest warriors"}
    ],
    
    "Master Devil Fruits": [
        {"level": 5, "reward": "Fruit Identification", "description": "Identify Devil Fruit types on sight"},
        {"level": 10, "reward": "Power Analysis", "description": "Understand Devil Fruit user abilities"},
        {"level": 20, "reward": "Rare Fruit Tracking", "description": "Track down legendary Devil Fruits"},
        {"level": 35, "reward": "Fruit Mastery Guide", "description": "Help others master their Devil Fruit powers"},
        {"level": 50, "reward": "Ultimate Fruit Knowledge", "description": "Understand the true nature of Devil Fruits"}
    ],
    
    "Topple the World Government": [
        {"level": 5, "reward": "Underground Network", "description": "Access to revolutionary information network"},
        {"level": 10, "reward": "Sabotage Skills", "description": "Learn to disrupt government operations"},
        {"level": 20, "reward": "Revolutionary Commander", "description": "Lead your own revolutionary cell"},
        {"level": 35, "reward": "Government Enemy", "description": "Become a high-priority target"},
        {"level": 50, "reward": "Revolutionary Hero", "description": "Lead the charge against the World Government"}
    ],
    
    "Become Pirate King": [
        {"level": 5, "reward": "Crew Leadership", "description": "Natural ability to lead and inspire crews"},
        {"level": 10, "reward": "Conqueror's Spirit", "description": "Intimidate weaker enemies without fighting"},
        {"level": 20, "reward": "Grand Line Navigator", "description": "Navigate the most dangerous seas"},
        {"level": 35, "reward": "Yonko Recognition", "description": "The Four Emperors acknowledge your strength"},
        {"level": 50, "reward": "One Piece Seeker", "description": "Begin the final quest to find One Piece"}
    ]
}

def get_dream_milestone(dream_name: str, level: int) -> dict:
    """Get the next milestone for a dream at a given level"""
    milestones = DREAM_MILESTONES.get(dream_name, [])
    
    for milestone in milestones:
        if milestone["level"] == level:
            return milestone
    
    return {}

def get_next_dream_milestone(dream_name: str, current_level: int) -> dict:
    """Get the next upcoming milestone for a dream"""
    milestones = DREAM_MILESTONES.get(dream_name, [])
    
    for milestone in milestones:
        if milestone["level"] > current_level:
            return milestone
    
    return {}

def get_dream_skills(dream_name: str) -> list:
    """Get skill trees associated with a dream"""
    dream_data = DREAMS.get(dream_name)
    if dream_data:
        return dream_data.get("skill_trees", [])
    return []

def get_dream_starting_bonus(dream_name: str) -> dict:
    """Get starting bonus for a dream"""
    dream_data = DREAMS.get(dream_name)
    if dream_data:
        return {
            "items": dream_data.get("starting_items", []),
            "stats": dream_data.get("stat_bonus", {}),
            "commands": dream_data.get("special_commands", [])
        }
    return {"items": [], "stats": {}, "commands": []}

def is_legendary_dream(dream_name: str) -> bool:
    """Check if a dream is legendary difficulty"""
    dream_data = DREAMS.get(dream_name)
    if dream_data:
        return dream_data.get("difficulty") == "legendary"
    return False
