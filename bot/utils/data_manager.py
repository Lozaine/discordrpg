"""
Data management utilities for character persistence
"""

import json
import os
import logging
from typing import List, Optional
from datetime import datetime

from ..models.character import Character
from config import Config

logger = logging.getLogger(__name__)

class DataManager:
    """Handles data persistence for characters"""
    
    def __init__(self):
        self.characters_file = Config.CHARACTERS_FILE
        self._ensure_data_file()
    
    def _ensure_data_file(self):
        """Ensure the characters data file exists"""
        if not os.path.exists(self.characters_file):
            os.makedirs(os.path.dirname(self.characters_file), exist_ok=True)
            self._save_data({})
    
    def _load_data(self) -> dict:
        """Load character data from file"""
        try:
            with open(self.characters_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load character data: {e}")
            return {}
    
    def _save_data(self, data: dict):
        """Save character data to file"""
        try:
            with open(self.characters_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Could not save character data: {e}")
            raise
    
    def save_character(self, character: Character):
        """Save a character to the data file"""
        data = self._load_data()
        
        user_id = character.user_id
        if user_id not in data:
            data[user_id] = []
        
        # Convert character to dict
        character_data = character.to_dict()
        
        # Check if character already exists (update)
        existing_index = None
        for i, existing_char in enumerate(data[user_id]):
            if existing_char['name'] == character.name:
                existing_index = i
                break
        
        if existing_index is not None:
            # Update existing character
            data[user_id][existing_index] = character_data
            logger.info(f"Updated character: {character.name} for user {user_id}")
        else:
            # Add new character
            data[user_id].append(character_data)
            logger.info(f"Saved new character: {character.name} for user {user_id}")
        
        self._save_data(data)
    
    def get_user_characters(self, user_id: str) -> List[Character]:
        """Get all characters for a user"""
        data = self._load_data()
        
        if user_id not in data:
            return []
        
        characters = []
        for char_data in data[user_id]:
            try:
                character = Character.from_dict(char_data)
                characters.append(character)
            except Exception as e:
                logger.warning(f"Could not load character data: {e}")
                continue
        
        return characters
    
    def get_character(self, user_id: str, character_name: str) -> Optional[Character]:
        """Get a specific character by name"""
        characters = self.get_user_characters(user_id)
        
        for character in characters:
            if character.name.lower() == character_name.lower():
                return character
        
        return None
    
    def delete_character(self, user_id: str, character_name: str) -> bool:
        """Delete a character"""
        data = self._load_data()
        
        if user_id not in data:
            return False
        
        # Find and remove character
        user_characters = data[user_id]
        for i, char_data in enumerate(user_characters):
            if char_data['name'].lower() == character_name.lower():
                del user_characters[i]
                self._save_data(data)
                logger.info(f"Deleted character: {character_name} for user {user_id}")
                return True
        
        return False
    
    def get_all_characters(self) -> List[Character]:
        """Get all characters from all users (for admin purposes)"""
        data = self._load_data()
        all_characters = []
        
        for user_id, user_characters in data.items():
            for char_data in user_characters:
                try:
                    character = Character.from_dict(char_data)
                    all_characters.append(character)
                except Exception as e:
                    logger.warning(f"Could not load character data: {e}")
                    continue
        
        return all_characters
    
    def backup_data(self, backup_path: str):
        """Create a backup of character data"""
        try:
            data = self._load_data()
            
            # Add timestamp to backup
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "characters": data
            }
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data backed up to: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
    
    def restore_data(self, backup_path: str):
        """Restore data from backup"""
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Extract character data
            if "characters" in backup_data:
                characters_data = backup_data["characters"]
            else:
                characters_data = backup_data  # Assume old format
            
            self._save_data(characters_data)
            logger.info(f"Data restored from: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
