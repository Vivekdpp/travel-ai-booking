#!/usr/bin/env python
"""
CLI Demo script for TravelAI Booking System
Run this to interactively test agents
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import settings
from src.database import db, init_db, close_db
from src.embeddings import kb, init_kb
from src.orchestrator import orchestrator


async def main():
    """Main demo function"""
    
    print("\n" + "="*60)
    print("🌍 Welcome to TravelAI Booking System!")
    print("="*60)
    print("\nMulti-Agent AI Travel Booking & Planning Platform")
    print("Powered by Claude API")
    print("\n" + "="*60)
    
    # Initialize system
    print("\n🔧 Initializing system...")
    try:
        await init_db()
        await init_kb()
        print("✓ System ready!\n")
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        return
    
    # Create demo user
    print("👤 Creating demo user...")
    try:
        user_id = await db.save_user(
            email="demo@travelai.com",
            name="Demo User",
            preferences={"budget": "mid-range", "travel_style": "adventure"}
        )
        print(f"✓ User created (ID: {user_id})\n")
    except Exception as e:
        print(f"✗ Error creating user: {e}")
        return
    
    # Demo conversations
    demo_conversations = [
        "Show me flights from Toronto to New York on April 15",
        "What hotels are available in Manhattan from April 15-20?",
        "Create an itinerary for my NYC trip",
        "Recommend a relaxing beach destination for 5 days under $2000"
    ]
    
    print("="*60)
    print("📝 DEMO CONVERSATIONS")
    print("="*60)
    
    for i, user_message in enumerate(demo_conversations, 1):
        print(f"\n[{i}] User: {user_message}")
        print("-" * 60)
        
        try:
            result = await orchestrator.handle_user_request(
                user_id=user_id,
                user_message=user_message
            )
            
            agent = result.get("agent", "unknown")
            response = result.get("response", "")
            
            print(f"Agent: {agent.upper()}")
            print(f"Response:\n{response}\n")
            
        except Exception as e:
            print(f"Error: {e}\n")
    
    # Interactive mode
    print("\n" + "="*60)
    print("💬 INTERACTIVE MODE")
    print("="*60)
    print("Type your travel requests (or 'quit' to exit)\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() == "quit":
                print("\n👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print("\n🤔 Processing...")
            result = await orchestrator.handle_user_request(
                user_id=user_id,
                user_message=user_input
            )
            
            agent = result.get("agent", "unknown")
            response = result.get("response", "")
            
            print(f"\n🤖 [{agent.upper()}]")
            print(f"{response}\n")
            print("-" * 60)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    await close_db()
    print("✓ Done!\n")


if __name__ == "__main__":
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not set!")
        print("Please set your API key: export ANTHROPIC_API_KEY=your_key")
        sys.exit(1)
    
    # Check database
    if not os.getenv("DATABASE_URL"):
        print("❌ Error: DATABASE_URL not set!")
        print("Please set database URL: export DATABASE_URL=postgresql://...")
        sys.exit(1)
    
    # Run demo
    asyncio.run(main())
