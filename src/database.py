"""
Database module for TravelAI Booking System
Handles PostgreSQL connections with async support
"""

import asyncpg
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.config import settings


class Database:
    """Async PostgreSQL database handler"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create database connection pool"""
        self.pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=settings.database_pool_size,
            max_size=settings.database_pool_size + settings.database_max_overflow,
            command_timeout=60,
        )
        print(f"✓ Database connected: {settings.database_url}")
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            print("✓ Database disconnected")
    
    async def execute(self, query: str, *args) -> str:
        """Execute a query (INSERT, UPDATE, DELETE)"""
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)
    
    async def fetch_one(self, query: str, *args) -> Optional[Dict]:
        """Fetch a single row"""
        async with self.pool.acquire() as connection:
            row = await connection.fetchrow(query, *args)
            return dict(row) if row else None
    
    async def fetch_all(self, query: str, *args) -> List[Dict]:
        """Fetch multiple rows"""
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def fetch_val(self, query: str, *args) -> Any:
        """Fetch a single value"""
        async with self.pool.acquire() as connection:
            return await connection.fetchval(query, *args)
    
    async def save_user(self, email: str, name: str, preferences: Dict = None) -> int:
        """Create or update user"""
        prefs_json = json.dumps(preferences or {})
        user_id = await self.fetch_val("""
            INSERT INTO users (email, name, preferences, created_at)
            VALUES ($1, $2, $3, NOW())
            ON CONFLICT (email) DO UPDATE
            SET name = $2, preferences = $3, updated_at = NOW()
            RETURNING id
        """, email, name, prefs_json)
        return user_id
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        return await self.fetch_one("SELECT * FROM users WHERE id = $1", user_id)
    
    async def save_search(self, user_id: int, search_type: str, query: Dict, results: Dict) -> int:
        """Save search results"""
        search_id = await self.fetch_val("""
            INSERT INTO searches (user_id, search_type, query, results, created_at)
            VALUES ($1, $2, $3, $4, NOW())
            RETURNING id
        """, user_id, search_type, json.dumps(query), json.dumps(results))
        return search_id
    
    async def save_booking(self, user_id: int, booking_type: str, details: Dict, status: str = "pending") -> int:
        """Save booking"""
        booking_id = await self.fetch_val("""
            INSERT INTO bookings (user_id, booking_type, booking_details, status, created_at, updated_at)
            VALUES ($1, $2, $3, $4, NOW(), NOW())
            RETURNING id
        """, user_id, booking_type, json.dumps(details), status)
        return booking_id
    
    async def get_booking(self, booking_id: int) -> Optional[Dict]:
        """Get booking by ID"""
        return await self.fetch_one("SELECT * FROM bookings WHERE id = $1", booking_id)
    
    async def get_user_bookings(self, user_id: int) -> List[Dict]:
        """Get all bookings for a user"""
        return await self.fetch_all("SELECT * FROM bookings WHERE user_id = $1 ORDER BY created_at DESC", user_id)
    
    async def save_itinerary(self, user_id: int, trip_name: str, start_date: str, end_date: str) -> int:
        """Create itinerary"""
        itinerary_id = await self.fetch_val("""
            INSERT INTO itineraries (user_id, trip_name, start_date, end_date, created_at, updated_at)
            VALUES ($1, $2, $3, $4, NOW(), NOW())
            RETURNING id
        """, user_id, trip_name, start_date, end_date)
        return itinerary_id
    
    async def save_conversation(self, user_id: int, agent_name: str, role: str, message: str, context: Dict = None) -> int:
        """Save conversation message"""
        msg_id = await self.fetch_val("""
            INSERT INTO conversations (user_id, agent_name, role, message, context, created_at)
            VALUES ($1, $2, $3, $4, $5, NOW())
            RETURNING id
        """, user_id, agent_name, role, message, json.dumps(context or {}))
        return msg_id
    
    async def get_conversation_history(self, user_id: int, agent_name: str, limit: int = 20) -> List[Dict]:
        """Get conversation history for an agent"""
        return await self.fetch_all("""
            SELECT * FROM conversations
            WHERE user_id = $1 AND agent_name = $2
            ORDER BY created_at DESC
            LIMIT $3
        """, user_id, agent_name, limit)


# Global database instance
db = Database()


async def init_db():
    """Initialize database on startup"""
    await db.connect()


async def close_db():
    """Close database on shutdown"""
    await db.disconnect()
