import asyncpg
from typing import List, Optional
from ..models.character import Character
from db.db import get_db_pool

class PostgresDataManager:
    """Handles data persistence for characters using PostgreSQL"""

    def __init__(self, pool=None):
        self.pool = pool

    async def init_pool(self):
        if not self.pool:
            self.pool = await get_db_pool()

    async def save_character(self, character: Character):
        await self.init_pool()
        async with self.pool.acquire() as conn:
            # Ensure user exists
            await conn.execute(
                """
                INSERT INTO users (discord_id, username)
                VALUES ($1, $2)
                ON CONFLICT (discord_id) DO NOTHING
                """,
                character.user_id, getattr(character, 'username', None)
            )
            # Upsert character
            await conn.execute(
                """
                INSERT INTO characters (user_id, name, race, origin, dream)
                VALUES ((SELECT id FROM users WHERE discord_id=$1), $2, $3, $4, $5)
                ON CONFLICT (user_id, name) DO UPDATE SET race=$3, origin=$4, dream=$5
                """,
                character.user_id, character.name, character.race, character.origin, character.dream
            )

    async def get_user_characters(self, user_id: str) -> List[Character]:
        await self.init_pool()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT c.* FROM characters c
                JOIN users u ON c.user_id = u.id
                WHERE u.discord_id = $1
                """,
                user_id
            )
            return [Character.from_dict(dict(row)) for row in rows]

    async def get_character(self, user_id: str, character_name: str) -> Optional[Character]:
        await self.init_pool()
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT c.* FROM characters c
                JOIN users u ON c.user_id = u.id
                WHERE u.discord_id = $1 AND c.name ILIKE $2
                """,
                user_id, character_name
            )
            if row:
                return Character.from_dict(dict(row))
            return None

    async def delete_character(self, user_id: str, character_name: str) -> bool:
        await self.init_pool()
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM characters
                WHERE user_id = (SELECT id FROM users WHERE discord_id=$1)
                AND name ILIKE $2
                """,
                user_id, character_name
            )
            return result[-1] != '0'

    async def get_all_characters(self) -> List[Character]:
        await self.init_pool()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM characters")
            return [Character.from_dict(dict(row)) for row in rows]
