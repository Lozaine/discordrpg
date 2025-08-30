"""
Extended data management for new systems
"""

import json
import os
import logging
from typing import List, Optional, Dict
from datetime import datetime

from .data_manager import DataManager
from ..models.crew import Crew
from ..models.ship import Ship
from ..models.quest import Quest, PlayerQuest, EAST_BLUE_QUESTS
from ..models.ally import Ally, PlayerAlly, AVAILABLE_ALLIES
from ..models.faction import FactionReputation
from config import Config

logger = logging.getLogger(__name__)

class SystemManager(DataManager):
    """Extended data manager for all RPG systems"""
    
    def __init__(self):
        super().__init__()
        self.crews_file = "data/crews.json"
        self.ships_file = "data/ships.json"
        self.quests_file = "data/quests.json"
        self.allies_file = "data/allies.json"
        self.reputation_file = "data/reputation.json"
        self._ensure_system_files()
    
    def _ensure_system_files(self):
        """Ensure all system data files exist"""
        system_files = [
            self.crews_file,
            self.ships_file, 
            self.quests_file,
            self.allies_file,
            self.reputation_file
        ]
        
        for file_path in system_files:
            if not os.path.exists(file_path):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
    
    # Crew Management
    def save_crew(self, crew: Crew):
        """Save a crew to the data file"""
        try:
            with open(self.crews_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        
        data[crew.crew_id] = crew.to_dict()
        
        with open(self.crews_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved crew: {crew.name} ({crew.crew_id})")
    
    def get_crew(self, crew_id: str) -> Optional[Crew]:
        """Get a crew by ID"""
        try:
            with open(self.crews_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if crew_id in data:
                return Crew.from_dict(data[crew_id])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load crew data: {e}")
        
        return None
    
    def get_all_crews(self) -> List[Crew]:
        """Get all crews"""
        try:
            with open(self.crews_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            crews = []
            for crew_data in data.values():
                try:
                    crews.append(Crew.from_dict(crew_data))
                except Exception as e:
                    logger.warning(f"Could not load crew: {e}")
            
            return crews
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def delete_crew(self, crew_id: str) -> bool:
        """Delete a crew"""
        try:
            with open(self.crews_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if crew_id in data:
                del data[crew_id]
                
                with open(self.crews_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Deleted crew: {crew_id}")
                return True
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Could not delete crew: {e}")
        
        return False
    
    # Ship Management
    def save_ship(self, ship: Ship):
        """Save a ship to the data file"""
        try:
            with open(self.ships_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        
        data[ship.ship_id] = ship.to_dict()
        
        with open(self.ships_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved ship: {ship.name} ({ship.ship_id})")
    
    def get_ship(self, ship_id: str) -> Optional[Ship]:
        """Get a ship by ID"""
        try:
            with open(self.ships_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if ship_id in data:
                return Ship.from_dict(data[ship_id])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load ship data: {e}")
        
        return None
    
    def get_character_ship(self, user_id: str, character_name: str) -> Optional[Ship]:
        """Get a character's ship through their crew"""
        # First check if character has a crew
        character = self.get_character(user_id, character_name)
        if not character or not character.crew_id:
            return None
        
        # Get crew and then ship
        crew = self.get_crew(character.crew_id)
        if not crew or not crew.ship_id:
            return None
        
        return self.get_ship(crew.ship_id)
    
    # Quest Management
    def get_available_quests(self, user_id: str, character_name: str) -> List[Quest]:
        """Get available quests for a character"""
        character = self.get_character(user_id, character_name)
        if not character:
            return []
        
        completed_quests = character.quests_completed
        available = []
        
        for quest in EAST_BLUE_QUESTS.values():
            if quest.is_available_for_character(character, completed_quests):
                available.append(quest)
        
        return available
    
    def start_quest(self, user_id: str, character_name: str, quest_id: str) -> bool:
        """Start a quest for a character"""
        if quest_id not in EAST_BLUE_QUESTS:
            return False
        
        # Check if quest is available
        available_quests = self.get_available_quests(user_id, character_name)
        quest = next((q for q in available_quests if q.quest_id == quest_id), None)
        
        if not quest:
            return False
        
        # Create player quest instance
        player_quest = PlayerQuest(
            user_id=user_id,
            character_name=character_name,
            quest_id=quest_id
        )
        
        # Save quest
        self.save_player_quest(player_quest)
        logger.info(f"Started quest {quest_id} for {character_name}")
        return True
    
    def save_player_quest(self, player_quest: PlayerQuest):
        """Save a player's quest progress"""
        try:
            with open(self.quests_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        
        user_data = data.get(player_quest.user_id, {})
        user_data[player_quest.quest_id] = player_quest.to_dict()
        data[player_quest.user_id] = user_data
        
        with open(self.quests_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_player_quests(self, user_id: str) -> List[PlayerQuest]:
        """Get all quests for a player"""
        try:
            with open(self.quests_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if user_id not in data:
                return []
            
            quests = []
            for quest_data in data[user_id].values():
                try:
                    quests.append(PlayerQuest.from_dict(quest_data))
                except Exception as e:
                    logger.warning(f"Could not load player quest: {e}")
            
            return quests
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    # Ally Management
    def recruit_ally(self, user_id: str, character_name: str, ally_id: str) -> bool:
        """Recruit an ally for a character"""
        if ally_id not in AVAILABLE_ALLIES:
            return False
        
        # Check if already recruited
        player_allies = self.get_player_allies(user_id)
        if any(ally.ally_id == ally_id for ally in player_allies):
            return False
        
        # Create player ally instance
        player_ally = PlayerAlly(
            user_id=user_id,
            character_name=character_name,
            ally_id=ally_id
        )
        
        self.save_player_ally(player_ally)
        logger.info(f"Recruited ally {ally_id} for {character_name}")
        return True
    
    def save_player_ally(self, player_ally: PlayerAlly):
        """Save a player's ally"""
        try:
            with open(self.allies_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        
        user_data = data.get(player_ally.user_id, [])
        # Remove existing ally if updating
        user_data = [ally for ally in user_data if ally.get('ally_id') != player_ally.ally_id]
        user_data.append(player_ally.to_dict())
        data[player_ally.user_id] = user_data
        
        with open(self.allies_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_player_allies(self, user_id: str) -> List[PlayerAlly]:
        """Get all allies for a player"""
        try:
            with open(self.allies_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if user_id not in data:
                return []
            
            allies = []
            for ally_data in data[user_id]:
                try:
                    allies.append(PlayerAlly.from_dict(ally_data))
                except Exception as e:
                    logger.warning(f"Could not load player ally: {e}")
            
            return allies
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    # Reputation Management
    def get_faction_reputation(self, user_id: str, character_name: str) -> Dict[str, FactionReputation]:
        """Get all faction reputations for a character"""
        try:
            with open(self.reputation_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            user_key = f"{user_id}_{character_name}"
            if user_key not in data:
                return {}
            
            reputations = {}
            for faction_data in data[user_key].values():
                try:
                    rep = FactionReputation.from_dict(faction_data)
                    reputations[rep.faction_name] = rep
                except Exception as e:
                    logger.warning(f"Could not load faction reputation: {e}")
            
            return reputations
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def update_faction_reputation(self, user_id: str, character_name: str, 
                                 faction: str, change: int, reason: str = "") -> List[str]:
        """Update faction reputation and return new milestones"""
        # Get existing reputation
        all_reps = self.get_faction_reputation(user_id, character_name)
        
        if faction not in all_reps:
            all_reps[faction] = FactionReputation(
                user_id=user_id,
                character_name=character_name,
                faction_name=faction
            )
        
        # Update reputation
        new_milestones = all_reps[faction].add_reputation(change, reason)
        
        # Save updated reputation
        self.save_faction_reputation(all_reps)
        
        logger.info(f"Updated {faction} reputation for {character_name}: {change:+d}")
        return new_milestones
    
    def save_faction_reputation(self, reputations: Dict[str, FactionReputation]):
        """Save faction reputations"""
        if not reputations:
            return
        
        # Get user info from first reputation
        first_rep = next(iter(reputations.values()))
        user_key = f"{first_rep.user_id}_{first_rep.character_name}"
        
        try:
            with open(self.reputation_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        
        user_data = {}
        for faction, rep in reputations.items():
            user_data[faction] = rep.to_dict()
        
        data[user_key] = user_data
        
        with open(self.reputation_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)