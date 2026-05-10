"""
FastAPI server for TravelAI Booking System
Provides REST API and WebSocket endpoints for agent interaction
"""

from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import asyncio
import logging
from datetime import datetime

from src.config import settings
from src.database import db, init_db, close_db
from src.embeddings import kb, init_kb
from src.orchestrator import orchestrator
from src.langchain_orchestrator import langchain_orchestrator

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="TravelAI Booking System",
    description="Multi-agent AI system for travel booking",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Startup/Shutdown ====================

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    logger.info("🚀 Starting TravelAI Booking System...")
    await init_db()
    await init_kb()
    logger.info("✓ System initialized successfully")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("⛔ Shutting down...")
    await close_db()
    logger.info("✓ Shutdown complete")

# ==================== Data Models ====================

class ChatRequest(BaseModel):
    user_id: int
    message: str
    mode: str = "custom"
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    user_id: int
    agent: str
    response: str
    timestamp: str
    status: str

class UserCreate(BaseModel):
    email: str
    name: str
    preferences: Optional[Dict] = None

class UserProfile(BaseModel):
    user_id: int
    email: str
    name: str
    preferences: Optional[Dict] = None
    created_at: Optional[str] = None

class BookingRequest(BaseModel):
    user_id: int
    booking_type: str  # 'flight', 'hotel', 'activity'
    booking_details: Dict

class ItineraryRequest(BaseModel):
    user_id: int
    trip_name: str
    start_date: str
    end_date: str
    activities: List[Dict]

# ==================== Health Check ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "TravelAI Booking System"
    }

# ==================== User Endpoints ====================

# ==================== User Endpoints ====================
@app.post("/api/users", response_model=UserProfile)
async def create_user(user: UserCreate):
    """Create a new user"""
    try:
        user_id = await db.save_user(
            email=user.email,
            name=user.name,
            preferences=user.preferences or {}
        )
        
        user_data = await db.get_user(user_id)
        
        # Parse preferences if it's a string
        preferences = user_data["preferences"]
        if isinstance(preferences, str):
            preferences = json.loads(preferences)
        
        return {
            "user_id": user_id,
            "email": user_data["email"],
            "name": user_data["name"],
            "preferences": preferences,
            "created_at": user_data["created_at"].isoformat() if user_data["created_at"] else None
        }
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/users/{user_id}", response_model=UserProfile)
async def get_user(user_id: int):
    """Get user profile"""
    try:
        user = await db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Parse preferences if it's a string
        preferences = user["preferences"]
        if isinstance(preferences, str):
            preferences = json.loads(preferences)
        
        return {
            "user_id": user_id,
            "email": user["email"],
            "name": user["name"],
            "preferences": preferences,
            "created_at": user["created_at"].isoformat() if user["created_at"] else None
        }
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== Chat Endpoints ====================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the agent system"""
    try:
        if request.mode == "langchain":
            result = await langchain_orchestrator.handle_user_request(
                user_id=request.user_id,
                user_message=request.message
            )
        else:
            result = await orchestrator.handle_user_request(
                user_id=request.user_id,
                user_message=request.message
            )
        
        return {
            "user_id": request.user_id,
            "agent": result.get("agent", "unknown"),
            "response": result.get("response", ""),
            "timestamp": result.get("timestamp", datetime.now().isoformat()),
            "status": result.get("status", "success")
        }
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Booking Endpoints ====================

@app.post("/api/bookings")
async def create_booking(booking: BookingRequest):
    """Create a new booking"""
    try:
        booking_id = await db.save_booking(
            user_id=booking.user_id,
            booking_type=booking.booking_type,
            details=booking.booking_details
        )
        
        booking_data = await db.get_booking(booking_id)
        
        return {
            "booking_id": booking_id,
            "status": "success",
            "booking_data": booking_data
        }
    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/bookings/{user_id}")
async def get_user_bookings(user_id: int):
    """Get all bookings for a user"""
    try:
        bookings = await db.get_user_bookings(user_id)
        return {
            "user_id": user_id,
            "total_bookings": len(bookings),
            "bookings": bookings
        }
    except Exception as e:
        logger.error(f"Error fetching bookings: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== Itinerary Endpoints ====================

@app.post("/api/itineraries")
async def create_itinerary(itinerary: ItineraryRequest):
    """Create a new itinerary"""
    try:
        itinerary_id = await db.save_itinerary(
            user_id=itinerary.user_id,
            trip_name=itinerary.trip_name,
            start_date=itinerary.start_date,
            end_date=itinerary.end_date
        )
        
        return {
            "itinerary_id": itinerary_id,
            "status": "created",
            "trip_name": itinerary.trip_name,
            "activities_count": len(itinerary.activities)
        }
    except Exception as e:
        logger.error(f"Error creating itinerary: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ==================== WebSocket Endpoint ====================

@app.websocket("/ws/chat/{user_id}")
async def websocket_chat(websocket: WebSocket, user_id: int):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    logger.info(f"✓ WebSocket connected for user {user_id}")
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            if not user_message:
                await websocket.send_json({
                    "status": "error",
                    "message": "Empty message"
                })
                continue
            
            # Send thinking message
            await websocket.send_json({
                "status": "thinking",
                "message": "🤔 Processing your request..."
            })
            
            # Process with orchestrator
            try:
                result = await orchestrator.handle_user_request(
                    user_id=user_id,
                    user_message=user_message
                )
                
                # Send response
                await websocket.send_json({
                    "status": "success",
                    "agent": result.get("agent"),
                    "response": result.get("response"),
                    "timestamp": result.get("timestamp")
                })
            
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                await websocket.send_json({
                    "status": "error",
                    "message": f"Error: {str(e)}"
                })
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        logger.info(f"✓ WebSocket disconnected for user {user_id}")

# ==================== Info Endpoint ====================

@app.get("/api/info")
async def system_info():
    """Get system information"""
    return {
        "name": "TravelAI Booking System",
        "version": "1.0.0",
        "description": "Multi-agent AI system for travel booking",
        "agents": [
            {
                "name": "search_agent",
                "description": "Searches for flights, hotels, and activities"
            },
            {
                "name": "booking_agent",
                "description": "Handles reservations and payments"
            },
            {
                "name": "itinerary_agent",
                "description": "Plans and optimizes travel schedules"
            },
            {
                "name": "recommendation_agent",
                "description": "Provides personalized suggestions"
            }
        ],
        "capabilities": [
            "Multi-agent orchestration",
            "Tool use and function calling",
            "Knowledge base queries",
            "Conversation memory",
            "Payment processing",
            "Itinerary optimization"
        ]
    }

# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "detail": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower()
    )
