"""
Quest system models and East Blue Saga implementation
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

class QuestStatus(Enum):
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    LOCKED = "locked"

class QuestType(Enum):
    MAIN_STORY = "main_story"
    SIDE_QUEST = "side_quest"
    DAILY = "daily"
    CREW_QUEST = "crew_quest"
    PVP_CHALLENGE = "pvp_challenge"

@dataclass
class QuestObjective:
    """Individual quest objective"""
    objective_id: str
    description: str
    objective_type: str  # kill, collect, talk, travel, survive, choose
    target: str = ""
    current_progress: int = 0
    required_progress: int = 1
    completed: bool = False
    
    def update_progress(self, amount: int = 1) -> bool:
        """Update objective progress. Returns True if completed."""
        self.current_progress = min(self.current_progress + amount, self.required_progress)
        if self.current_progress >= self.required_progress:
            self.completed = True
        return self.completed
    
    def to_dict(self) -> dict:
        return {
            "objective_id": self.objective_id,
            "description": self.description,
            "objective_type": self.objective_type,
            "target": self.target,
            "current_progress": self.current_progress,
            "required_progress": self.required_progress,
            "completed": self.completed
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'QuestObjective':
        return cls(
            objective_id=data["objective_id"],
            description=data["description"],
            objective_type=data["objective_type"],
            target=data.get("target", ""),
            current_progress=data.get("current_progress", 0),
            required_progress=data.get("required_progress", 1),
            completed=data.get("completed", False)
        )

@dataclass
class QuestReward:
    """Quest reward structure"""
    experience: int = 0
    bounty: int = 0
    berry: int = 0  # Currency
    items: Dict[str, int] = field(default_factory=dict)
    reputation: Dict[str, int] = field(default_factory=dict)  # faction reputation changes
    unlocks: List[str] = field(default_factory=list)  # Unlocked quests, abilities, etc.
    
    def to_dict(self) -> dict:
        return {
            "experience": self.experience,
            "bounty": self.bounty,
            "berry": self.berry,
            "items": self.items,
            "reputation": self.reputation,
            "unlocks": self.unlocks
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'QuestReward':
        return cls(
            experience=data.get("experience", 0),
            bounty=data.get("bounty", 0),
            berry=data.get("berry", 0),
            items=data.get("items", {}),
            reputation=data.get("reputation", {}),
            unlocks=data.get("unlocks", [])
        )

@dataclass
class Quest:
    """Main quest data structure"""
    quest_id: str
    title: str
    description: str
    saga: str = ""  # East Blue, Alabasta, etc.
    arc: str = ""   # Romance Dawn, Orange Town, etc.
    quest_type: QuestType = QuestType.MAIN_STORY
    
    # Quest requirements and availability
    level_requirement: int = 1
    origin_requirement: List[str] = field(default_factory=list)
    dream_requirement: List[str] = field(default_factory=list)
    faction_requirement: List[str] = field(default_factory=list)
    prerequisite_quests: List[str] = field(default_factory=list)
    
    # Quest objectives and progression
    objectives: List[QuestObjective] = field(default_factory=list)
    choices: Dict[str, Any] = field(default_factory=dict)  # Choice-based quest data
    
    # Rewards and consequences
    rewards: QuestReward = field(default_factory=QuestReward)
    failure_consequences: QuestReward = field(default_factory=QuestReward)
    
    # Time constraints
    time_limit: Optional[int] = None  # Minutes
    expires_at: Optional[datetime] = None
    
    # Quest metadata
    difficulty: str = "Easy"  # Easy, Medium, Hard, Legendary
    estimated_duration: int = 30  # Minutes
    
    def is_available_for_character(self, character, completed_quests: List[str]) -> bool:
        """Check if quest is available for a specific character"""
        # Level requirement
        if character.level < self.level_requirement:
            return False
        
        # Origin requirement
        if self.origin_requirement and character.origin not in self.origin_requirement:
            return False
        
        # Dream requirement
        if self.dream_requirement and character.dream not in self.dream_requirement:
            return False
        
        # Faction requirement
        if self.faction_requirement and character.faction not in self.faction_requirement:
            return False
        
        # Prerequisite quests
        for prereq in self.prerequisite_quests:
            if prereq not in completed_quests:
                return False
        
        return True
    
    def get_next_objective(self) -> Optional[QuestObjective]:
        """Get the next incomplete objective"""
        for objective in self.objectives:
            if not objective.completed:
                return objective
        return None
    
    def is_completed(self) -> bool:
        """Check if all objectives are completed"""
        return all(obj.completed for obj in self.objectives)
    
    def get_progress_percentage(self) -> float:
        """Get quest completion percentage"""
        if not self.objectives:
            return 0.0
        
        total_progress = sum(obj.current_progress for obj in self.objectives)
        total_required = sum(obj.required_progress for obj in self.objectives)
        
        if total_required == 0:
            return 100.0
        
        return (total_progress / total_required) * 100
    
    def to_dict(self) -> dict:
        return {
            "quest_id": self.quest_id,
            "title": self.title,
            "description": self.description,
            "saga": self.saga,
            "arc": self.arc,
            "quest_type": self.quest_type.value,
            "level_requirement": self.level_requirement,
            "origin_requirement": self.origin_requirement,
            "dream_requirement": self.dream_requirement,
            "faction_requirement": self.faction_requirement,
            "prerequisite_quests": self.prerequisite_quests,
            "objectives": [obj.to_dict() for obj in self.objectives],
            "choices": self.choices,
            "rewards": self.rewards.to_dict(),
            "failure_consequences": self.failure_consequences.to_dict(),
            "time_limit": self.time_limit,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "difficulty": self.difficulty,
            "estimated_duration": self.estimated_duration
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Quest':
        objectives = [QuestObjective.from_dict(obj_data) for obj_data in data.get("objectives", [])]
        
        return cls(
            quest_id=data["quest_id"],
            title=data["title"],
            description=data["description"],
            saga=data.get("saga", ""),
            arc=data.get("arc", ""),
            quest_type=QuestType(data.get("quest_type", "main_story")),
            level_requirement=data.get("level_requirement", 1),
            origin_requirement=data.get("origin_requirement", []),
            dream_requirement=data.get("dream_requirement", []),
            faction_requirement=data.get("faction_requirement", []),
            prerequisite_quests=data.get("prerequisite_quests", []),
            objectives=objectives,
            choices=data.get("choices", {}),
            rewards=QuestReward.from_dict(data.get("rewards", {})),
            failure_consequences=QuestReward.from_dict(data.get("failure_consequences", {})),
            time_limit=data.get("time_limit"),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            difficulty=data.get("difficulty", "Easy"),
            estimated_duration=data.get("estimated_duration", 30)
        )

@dataclass
class PlayerQuest:
    """Player's active quest instance"""
    user_id: str
    character_name: str
    quest_id: str
    status: QuestStatus = QuestStatus.ACTIVE
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    choices_made: Dict[str, str] = field(default_factory=dict)
    objectives_state: List[dict] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "character_name": self.character_name,
            "quest_id": self.quest_id,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "choices_made": self.choices_made,
            "objectives_state": self.objectives_state
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PlayerQuest':
        return cls(
            user_id=data["user_id"],
            character_name=data["character_name"],
            quest_id=data["quest_id"],
            status=QuestStatus(data.get("status", "active")),
            started_at=datetime.fromisoformat(data["started_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            choices_made=data.get("choices_made", {}),
            objectives_state=data.get("objectives_state", [])
        )

# East Blue Saga Quest Definitions
EAST_BLUE_QUESTS = {
    # Romance Dawn Arc
    "romance_dawn_marine": Quest(
        quest_id="romance_dawn_marine",
        title="The Tyrant's Fall",
        description="Expose Captain Morgan's corruption in Shells Town and decide your path as a Marine.",
        saga="East Blue",
        arc="Romance Dawn",
        quest_type=QuestType.MAIN_STORY,
        origin_requirement=["Shells Town"],
        objectives=[
            QuestObjective("investigate_morgan", "Investigate Captain Morgan's activities", "investigate", "captain_morgan"),
            QuestObjective("gather_evidence", "Gather evidence of corruption", "collect", "evidence", 0, 3),
            QuestObjective("confront_morgan", "Confront Captain Morgan", "boss_fight", "morgan"),
            QuestObjective("make_choice", "Decide your path forward", "choose", "loyalty_choice")
        ],
        rewards=QuestReward(
            experience=500,
            bounty=0,  # Marines don't get bounties initially
            berry=5000,
            items={"Marine Sword": 1, "Evidence Documents": 1},
            reputation={"Marine": 100},
            unlocks=["marine_deserter_path", "loyal_marine_path"]
        ),
        difficulty="Medium",
        estimated_duration=45
    ),
    
    "romance_dawn_pirate": Quest(
        quest_id="romance_dawn_pirate",
        title="The Liar's Legacy",
        description="Help Usopp defend Syrup Village and earn your first ship.",
        saga="East Blue",
        arc="Romance Dawn",
        quest_type=QuestType.MAIN_STORY,
        origin_requirement=["Syrup Village"],
        objectives=[
            QuestObjective("meet_usopp", "Meet Usopp and learn his tales", "talk", "usopp"),
            QuestObjective("defend_village", "Help defend the village from pirates", "combat", "black_cat_pirates", 0, 5),
            QuestObjective("prove_worth", "Prove your worth to earn a ship", "challenge", "ship_trial"),
            QuestObjective("name_ship", "Name your new ship", "choose", "ship_name")
        ],
        rewards=QuestReward(
            experience=400,
            bounty=5000000,  # 5 million berry bounty
            berry=3000,
            items={"Small Ship": 1, "Pirate Flag": 1, "Navigation Tools": 1},
            reputation={"Pirate": 150},
            unlocks=["crew_formation", "grand_line_preparation"]
        ),
        difficulty="Medium",
        estimated_duration=40
    ),
    
    "romance_dawn_revolutionary": Quest(
        quest_id="romance_dawn_revolutionary",
        title="Whispers of Truth",
        description="Uncover government secrets and make contact with the Revolutionary Army.",
        saga="East Blue",
        arc="Romance Dawn",
        quest_type=QuestType.MAIN_STORY,
        origin_requirement=["Ohara"],
        objectives=[
            QuestObjective("find_message", "Find the hidden scholar's message", "investigate", "hidden_message"),
            QuestObjective("decode_cipher", "Decode the encrypted message", "puzzle", "cipher_puzzle"),
            QuestObjective("avoid_marines", "Avoid Marine patrols while investigating", "stealth", "marine_patrol", 0, 3),
            QuestObjective("contact_revolutionaries", "Make contact with Revolutionary agents", "talk", "revolutionary_contact")
        ],
        rewards=QuestReward(
            experience=450,
            bounty=3000000,  # Revolutionary bounty
            berry=4000,
            items={"Encrypted Documents": 1, "Revolutionary Communication Device": 1},
            reputation={"Revolutionary": 200, "World Government": -100},
            unlocks=["revolutionary_network", "government_enemy_status"]
        ),
        difficulty="Hard",
        estimated_duration=50
    ),
    
    "romance_dawn_cook": Quest(
        quest_id="romance_dawn_cook",
        title="A Taste of the Grand Line",
        description="Train as a cook at Baratie and defend against the Krieg Pirates.",
        saga="East Blue",
        arc="Romance Dawn",
        quest_type=QuestType.MAIN_STORY,
        origin_requirement=["Baratie"],
        objectives=[
            QuestObjective("cooking_training", "Complete cooking training", "skill", "cooking", 0, 5),
            QuestObjective("serve_customers", "Serve customers during busy periods", "minigame", "service", 0, 10),
            QuestObjective("cook_combat_food", "Prepare combat buffs during Krieg attack", "cooking", "combat_food", 0, 3),
            QuestObjective("defeat_krieg_pirates", "Help defeat the Krieg Pirates", "combat", "krieg_pirates", 0, 8)
        ],
        rewards=QuestReward(
            experience=400,
            bounty=2000000,
            berry=6000,
            items={"Professional Chef Knife": 1, "Recipe Collection": 1, "Combat Rations": 5},
            reputation={"Neutral": 100},
            unlocks=["advanced_cooking", "sanji_mentorship"]
        ),
        difficulty="Medium",
        estimated_duration=35
    ),
    
    # Orange Town Arc
    "orange_town_main": Quest(
        quest_id="orange_town_main",
        title="The Clown's Challenge",
        description="Deal with Buggy the Clown and his crew terrorizing Orange Town.",
        saga="East Blue",
        arc="Orange Town",
        quest_type=QuestType.MAIN_STORY,
        level_requirement=2,
        prerequisite_quests=["romance_dawn_marine", "romance_dawn_pirate", "romance_dawn_revolutionary", "romance_dawn_cook"],
        objectives=[
            QuestObjective("arrive_orange_town", "Arrive at Orange Town", "travel", "orange_town"),
            QuestObjective("assess_situation", "Assess the Buggy Pirates situation", "investigate", "buggy_situation"),
            QuestObjective("choose_approach", "Choose how to deal with Buggy", "choose", "buggy_approach"),
            QuestObjective("resolve_conflict", "Resolve the conflict with Buggy", "boss_fight", "buggy_boss")
        ],
        choices={
            "buggy_approach": {
                "fight": {
                    "description": "Fight Buggy directly in combat",
                    "consequences": {"bounty": 5000000, "reputation": {"Pirate": 100}},
                    "unlocks": ["devil_fruit_knowledge_combat"]
                },
                "outsmart": {
                    "description": "Try to outsmart and trick Buggy",
                    "consequences": {"experience": 200, "reputation": {"Neutral": 150}},
                    "unlocks": ["devil_fruit_knowledge_study"]
                },
                "negotiate": {
                    "description": "Attempt to negotiate with Buggy",
                    "consequences": {"berry": 10000, "reputation": {"Pirate": -50, "Neutral": 100}},
                    "unlocks": ["devil_fruit_information"]
                }
            }
        },
        rewards=QuestReward(
            experience=600,
            berry=8000,
            items={"Devil Fruit Guide": 1},
            unlocks=["syrup_village_access"]
        ),
        difficulty="Medium",
        estimated_duration=40
    ),
    
    # Syrup Village Arc
    "syrup_village_main": Quest(
        quest_id="syrup_village_main",
        title="The Usurper's Ruse",
        description="Help Usopp and Kaya against Captain Kuro's deceptive plan.",
        saga="East Blue",
        arc="Syrup Village",
        quest_type=QuestType.MAIN_STORY,
        level_requirement=3,
        prerequisite_quests=["orange_town_main"],
        objectives=[
            QuestObjective("meet_usopp_kaya", "Meet Usopp and learn about Kaya", "talk", "usopp"),
            QuestObjective("investigate_klahadore", "Investigate the butler Klahadore", "investigate", "klahadore"),
            QuestObjective("uncover_plan", "Uncover Captain Kuro's assassination plan", "investigate", "kuro_plan"),
            QuestObjective("form_alliance", "Form an alliance to stop Kuro", "choose", "alliance_type"),
            QuestObjective("final_battle", "Defeat Captain Kuro and his crew", "boss_fight", "kuro_crew")
        ],
        choices={
            "alliance_type": {
                "pirate_alliance": {
                    "description": "Alliance for treasure and adventure",
                    "requirements": {"faction": ["Pirate"]},
                    "consequences": {"items": {"Treasure Map": 1}, "bounty": 3000000}
                },
                "justice_alliance": {
                    "description": "Alliance to protect innocent villagers",
                    "requirements": {"faction": ["Marine", "Revolutionary"]},
                    "consequences": {"reputation": {"Village": 200}, "items": {"Village Thanks": 1}}
                },
                "marksman_connection": {
                    "description": "Connect with Usopp as a fellow marksman",
                    "requirements": {"dream": ["Brave Warrior of the Sea"]},
                    "consequences": {"unlocks": ["usopp_training"], "items": {"Marksman Training": 1}}
                }
            }
        },
        rewards=QuestReward(
            experience=750,
            berry=12000,
            items={"Kuro's Claws": 1},
            reputation={"Village": 150},
            unlocks=["baratie_access"]
        ),
        difficulty="Hard",
        estimated_duration=60
    ),
    
    # Baratie Arc
    "baratie_main": Quest(
        quest_id="baratie_main",
        title="The Pirate Restaurant",
        description="Experience the unique floating restaurant and face the Don Krieg Pirates.",
        saga="East Blue",
        arc="Baratie",
        quest_type=QuestType.MAIN_STORY,
        level_requirement=4,
        prerequisite_quests=["syrup_village_main"],
        objectives=[
            QuestObjective("arrive_baratie", "Arrive at the Baratie restaurant", "travel", "baratie"),
            QuestObjective("restaurant_experience", "Experience the unique restaurant", "interact", "baratie_staff"),
            QuestObjective("krieg_arrival", "Witness Don Krieg's arrival", "cutscene", "krieg_arrival"),
            QuestObjective("tactical_combat", "Engage in tactical combat with Krieg pirates", "combat", "krieg_tactical"),
            QuestObjective("environmental_advantage", "Use restaurant environment to your advantage", "strategy", "environment_use", 0, 3)
        ],
        rewards=QuestReward(
            experience=800,
            berry=15000,
            reputation={"Baratie": 200},
            unlocks=["arlong_park_access"]
        ),
        difficulty="Hard",
        estimated_duration=50
    ),
    
    "baratie_cooking_special": Quest(
        quest_id="baratie_cooking_special",
        title="Master Chef's Trial",
        description="Special cooking challenge for those who dream of finding All Blue.",
        saga="East Blue",
        arc="Baratie",
        quest_type=QuestType.SIDE_QUEST,
        level_requirement=4,
        dream_requirement=["Find the All Blue"],
        prerequisite_quests=["baratie_main"],
        objectives=[
            QuestObjective("cooking_challenge", "Complete the master cooking challenge", "minigame", "cooking_trial", 0, 5),
            QuestObjective("combat_cooking", "Prepare combat buffs under pressure", "cooking", "pressure_cooking", 0, 3),
            QuestObjective("sanji_approval", "Earn Sanji's approval", "achievement", "sanji_recognition")
        ],
        rewards=QuestReward(
            experience=400,
            items={"Sanji's Special Recipe": 1, "Master Chef's Knife": 1},
            unlocks=["advanced_cooking_tree", "sanji_training_access"]
        ),
        difficulty="Hard",
        estimated_duration=30
    ),
    
    # Arlong Park Arc
    "arlong_park_main": Quest(
        quest_id="arlong_park_main",
        title="The Weight of a Promise",
        description="Confront the Fish-Man Arlong and his oppression of Cocoyasi Village.",
        saga="East Blue",
        arc="Arlong Park",
        quest_type=QuestType.MAIN_STORY,
        level_requirement=5,
        prerequisite_quests=["baratie_main"],
        objectives=[
            QuestObjective("discover_oppression", "Discover Arlong's oppression of the village", "investigate", "arlong_oppression"),
            QuestObjective("moral_choice", "Make a moral choice about intervention", "choose", "intervention_choice"),
            QuestObjective("prepare_strategy", "Prepare strategy for confronting Arlong", "strategy", "arlong_strategy"),
            QuestObjective("defeat_crew", "Defeat Arlong's crew members", "combat", "arlong_crew", 0, 6),
            QuestObjective("final_arlong", "Face Arlong in final combat", "boss_fight", "arlong_final")
        ],
        choices={
            "intervention_choice": {
                "fight_arlong": {
                    "description": "Fight Arlong directly to free the village",
                    "consequences": {"bounty": 10000000, "reputation": {"Village": 300, "Fish-Man": -100}}
                },
                "work_with_marines": {
                    "description": "Work with Marines to stop Arlong legally",
                    "requirements": {"faction": ["Marine"]},
                    "consequences": {"reputation": {"Marine": 200, "World Government": 150}}
                },
                "ignore_situation": {
                    "description": "Ignore the situation and move on",
                    "consequences": {"reputation": {"Village": -200}, "berry": 5000}
                },
                "fishman_negotiation": {
                    "description": "Try to negotiate as a fellow Fish-Man",
                    "requirements": {"race": ["Fish-Man"]},
                    "consequences": {"reputation": {"Fish-Man": 100}, "unlocks": ["fishman_politics"]}
                }
            }
        },
        rewards=QuestReward(
            experience=1000,
            berry=20000,
            items={"Arlong's Saw Sword": 1},
            unlocks=["loguetown_access"]
        ),
        difficulty="Legendary",
        estimated_duration=75
    ),
    
    # Loguetown Arc
    "loguetown_main": Quest(
        quest_id="loguetown_main",
        title="The Final Stand",
        description="Face your final test in the town where the Pirate King died, before entering the Grand Line.",
        saga="East Blue",
        arc="Loguetown",
        quest_type=QuestType.MAIN_STORY,
        level_requirement=6,
        prerequisite_quests=["arlong_park_main"],
        objectives=[
            QuestObjective("arrive_loguetown", "Arrive at Loguetown, the town of beginning and end", "travel", "loguetown"),
            QuestObjective("execution_platform", "Visit Gol D. Roger's execution platform", "visit", "execution_platform"),
            QuestObjective("final_preparation", "Make final preparations for the Grand Line", "prepare", "grand_line_prep"),
            QuestObjective("faction_choice", "Make your final faction choice", "choose", "final_faction"),
            QuestObjective("smoker_encounter", "Face Captain Smoker or other Marine forces", "boss_fight", "smoker_battle"),
            QuestObjective("escape_pursuit", "Escape pursuit and reach the Grand Line", "escape", "grand_line_escape")
        ],
        choices={
            "final_faction": {
                "dedicated_pirate": {
                    "description": "Commit fully to the pirate life",
                    "consequences": {"bounty": 15000000, "reputation": {"Pirate": 500}}
                },
                "marine_officer": {
                    "description": "Become a dedicated Marine officer",
                    "consequences": {"reputation": {"Marine": 500}, "unlocks": ["marine_grand_line"]}
                },
                "revolutionary": {
                    "description": "Join the Revolutionary Army fully",
                    "consequences": {"reputation": {"Revolutionary": 500}, "unlocks": ["revolutionary_missions"]}
                },
                "independent": {
                    "description": "Remain independent and neutral",
                    "consequences": {"reputation": {"Neutral": 300}, "unlocks": ["freelancer_path"]}
                }
            }
        },
        rewards=QuestReward(
            experience=1200,
            berry=25000,
            items={"Grand Line Log Pose": 1, "Execution Platform Fragment": 1},
            unlocks=["grand_line_access", "reverse_mountain_passage"]
        ),
        difficulty="Legendary",
        estimated_duration=90
    ),

    # World Government Arc
    "east_blue_world_gov": Quest(
        quest_id="east_blue_world_gov",
        title="Cipher Pol's Secret",
        description="Assist Cipher Pol in uncovering a rogue scholar cell in East Blue. Stealth, investigation, and a code-breaking minigame await.",
        saga="East Blue",
        arc="Cipher Pol Mission",
        quest_type=QuestType.MAIN_STORY,
        faction_requirement=["World Government"],
        objectives=[
            QuestObjective("meet_cipher_pol", "Meet with Cipher Pol agent at Loguetown", "talk", "cipher_pol_agent"),
            QuestObjective("investigate_scholars", "Investigate suspicious activities in the library", "investigate", "library"),
            QuestObjective("code_breaking", "Crack the scholar's encrypted message (minigame)", "minigame", "code_breaking"),
            QuestObjective("capture_rogues", "Capture rogue scholars hiding in the port", "combat", "rogue_scholars", 0, 3)
        ],
        rewards=QuestReward(
            experience=500,
            berry=7000,
            items={"Cipher Pol Badge": 1, "Encrypted Scroll": 1},
            reputation={"World Government": 150},
            unlocks=["cipher_pol_network"]
        ),
        difficulty="Medium",
        estimated_duration=40
    ),

    # Neutral Arc
    "east_blue_neutral": Quest(
        quest_id="east_blue_neutral",
        title="Merchant's Dilemma",
        description="Help a merchant navigate trade disputes and defend against bandits. Includes a trade minigame and diplomacy choices.",
        saga="East Blue",
        arc="Trade Routes",
        quest_type=QuestType.MAIN_STORY,
        faction_requirement=["Neutral"],
        objectives=[
            QuestObjective("meet_merchant", "Meet the merchant at Orange Town", "talk", "merchant"),
            QuestObjective("trade_minigame", "Negotiate trade deals (minigame)", "minigame", "trade_negotiation"),
            QuestObjective("defend_convoy", "Defend the merchant's convoy from bandits", "combat", "bandits", 0, 4),
            QuestObjective("diplomacy", "Resolve a dispute between rival traders", "choose", "diplomacy_choice")
        ],
        rewards=QuestReward(
            experience=400,
            berry=9000,
            items={"Trade Permit": 1, "Rare Goods": 2},
            reputation={"Neutral": 120},
            unlocks=["trade_network"]
        ),
        difficulty="Easy",
        estimated_duration=35
    ),

    # Village Arc
    "east_blue_village": Quest(
        quest_id="east_blue_village",
        title="Defend the Village",
        description="Bandits threaten a peaceful village. Gather resources, build barricades (minigame), and fight off the attackers.",
        saga="East Blue",
        arc="Village Defense",
        quest_type=QuestType.MAIN_STORY,
        faction_requirement=["Village"],
        objectives=[
            QuestObjective("warn_villagers", "Warn villagers of the coming attack", "talk", "villagers"),
            QuestObjective("gather_resources", "Gather wood and supplies for barricades", "collect", "resources", 0, 5),
            QuestObjective("build_barricades", "Build barricades (minigame)", "minigame", "barricade_building"),
            QuestObjective("fight_bandits", "Fight off the bandit attack", "combat", "bandits", 0, 6)
        ],
        rewards=QuestReward(
            experience=350,
            berry=4000,
            items={"Village Thanks": 1, "Defender's Medal": 1},
            reputation={"Village": 200},
            unlocks=["village_protector"]
        ),
        difficulty="Easy",
        estimated_duration=30
    ),

    # Fish-Man Arc
    "east_blue_fishman": Quest(
        quest_id="east_blue_fishman",
        title="Tides of Change",
        description="Help Fish-Man communities with ocean navigation, face hostile fishermen, and negotiate peace. Includes an ocean minigame.",
        saga="East Blue",
        arc="Fish-Man Community",
        quest_type=QuestType.MAIN_STORY,
        faction_requirement=["Fish-Man"],
        objectives=[
            QuestObjective("ocean_navigation", "Navigate treacherous waters (minigame)", "minigame", "ocean_navigation"),
            QuestObjective("hostile_fishermen", "Defeat hostile fishermen threatening the community", "combat", "hostile_fishermen", 0, 4),
            QuestObjective("negotiate_peace", "Negotiate peace with local humans", "choose", "peace_negotiation")
        ],
        rewards=QuestReward(
            experience=450,
            berry=8000,
            items={"Ocean Chart": 1, "Fish-Man Token": 1},
            reputation={"Fish-Man": 150, "Village": 50},
            unlocks=["fishman_diplomacy"]
        ),
        difficulty="Medium",
        estimated_duration=40
    ),

    # Mink Arc
    "east_blue_mink": Quest(
        quest_id="east_blue_mink",
        title="Storm on the Horizon",
        description="A sudden storm threatens Zou's travelers. Master a weather minigame, fight pirates, and train your Electro skills.",
        saga="East Blue",
        arc="Mink Adventure",
        quest_type=QuestType.MAIN_STORY,
        faction_requirement=["Mink"],
        objectives=[
            QuestObjective("weather_minigame", "Navigate the storm (minigame)", "minigame", "weather_navigation"),
            QuestObjective("fight_pirates", "Defeat pirates preying on travelers", "combat", "storm_pirates", 0, 5),
            QuestObjective("electro_training", "Train your Electro abilities", "skill", "electro_training", 0, 3)
        ],
        rewards=QuestReward(
            experience=500,
            berry=10000,
            items={"Electro Gem": 1, "Storm Cloak": 1},
            reputation={"Mink": 150},
            unlocks=["electro_mastery"]
        ),
        difficulty="Medium",
        estimated_duration=45
    )
}

def get_quests_for_origin(origin: str) -> List[Quest]:
    """Get available quests for a specific origin"""
    available_quests = []
    for quest in EAST_BLUE_QUESTS.values():
        if not quest.origin_requirement or origin in quest.origin_requirement:
            available_quests.append(quest)
    return available_quests

def get_quest_chain(starting_quest_id: str) -> List[str]:
    """Get the quest chain starting from a specific quest"""
    chain = [starting_quest_id]
    current_quest = starting_quest_id
    
    # Find quests that have this as a prerequisite
    while True:
        next_quest = None
        for quest_id, quest in EAST_BLUE_QUESTS.items():
            if current_quest in quest.prerequisite_quests:
                next_quest = quest_id
                break
        
        if next_quest and next_quest not in chain:
            chain.append(next_quest)
            current_quest = next_quest
        else:
            break
    
    return chain