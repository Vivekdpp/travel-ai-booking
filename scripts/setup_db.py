"""
Database initialization script for TravelAI Booking System
Creates all necessary tables and schema
"""

import asyncio
import asyncpg
from src.config import settings

async def init_database():
    """Create all database tables"""
    
    # Connect to database
    conn = await asyncpg.connect(settings.database_url)
    
    print("🔧 Initializing database schema...")
    
    try:
        # Create USERS table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255),
                preferences JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """)
        print("✓ Created users table")
        
        # Create SEARCHES table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(id) ON DELETE CASCADE,
                search_type VARCHAR(50),
                query JSONB,
                results JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_searches_user_id ON searches(user_id);
            CREATE INDEX IF NOT EXISTS idx_searches_created_at ON searches(created_at);
        """)
        print("✓ Created searches table")
        
        # Create BOOKINGS table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(id) ON DELETE CASCADE,
                booking_type VARCHAR(50),
                booking_details JSONB,
                status VARCHAR(50) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);
            CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
        """)
        print("✓ Created bookings table")
        
        # Create ITINERARIES table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS itineraries (
                id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(id) ON DELETE CASCADE,
                trip_name VARCHAR(255),
                start_date DATE,
                end_date DATE,
                activities JSONB DEFAULT '[]',
                total_cost DECIMAL(10, 2),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_itineraries_user_id ON itineraries(user_id);
        """)
        print("✓ Created itineraries table")
        
        # Create CONVERSATIONS table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                user_id INT REFERENCES users(id) ON DELETE CASCADE,
                agent_name VARCHAR(100),
                role VARCHAR(20),
                message TEXT,
                context JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS idx_conversations_user_agent ON conversations(user_id, agent_name);
            CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
        """)
        print("✓ Created conversations table")
        
        print("\n✅ Database initialization complete!")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise
    
    finally:
        await conn.close()

async def drop_all_tables():
    """Drop all tables (for development/testing)"""
    
    conn = await asyncpg.connect(settings.database_url)
    
    print("⚠️  Dropping all tables...")
    
    try:
        await conn.execute("""
            DROP TABLE IF EXISTS conversations CASCADE;
            DROP TABLE IF EXISTS itineraries CASCADE;
            DROP TABLE IF EXISTS bookings CASCADE;
            DROP TABLE IF EXISTS searches CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
        """)
        print("✓ All tables dropped")
    except Exception as e:
        print(f"Error dropping tables: {e}")
    finally:
        await conn.close()

async def reset_database():
    """Reset database by dropping and recreating all tables"""
    await drop_all_tables()
    await init_database()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        asyncio.run(reset_database())
    else:
        asyncio.run(init_database())
