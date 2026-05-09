"""
Agent Orchestrator for TravelAI Booking System
Coordinates all agents and routes user requests to appropriate handlers
"""

from typing import Dict, Optional
from src.agents.search_agent import SearchAgent
from src.agents.booking_agent import BookingAgent
from src.agents.itinerary_agent import ItineraryAgent
from src.agents.recommendation_agent import RecommendationAgent
from src.embeddings import kb
from src.database import db


class Orchestrator:
    """Coordinates all agents and manages multi-agent workflows"""
    
    def __init__(self):
        self.search_agent = SearchAgent()
        self.booking_agent = BookingAgent()
        self.itinerary_agent = ItineraryAgent()
        self.recommendation_agent = RecommendationAgent()
        self.agents = {
            "search": self.search_agent,
            "booking": self.booking_agent,
            "itinerary": self.itinerary_agent,
            "recommendation": self.recommendation_agent
        }
    
    async def classify_intent(self, user_message: str) -> str:
        """Classify user intent to route to appropriate agent"""
        
        message_lower = user_message.lower()
        
        # Intent keywords mapping
        search_keywords = ["search", "find", "look for", "show me", "available", "options", "flights", "hotels", "activities"]
        booking_keywords = ["book", "reserve", "confirm", "payment", "pay", "checkout", "complete"]
        itinerary_keywords = ["plan", "itinerary", "schedule", "organize", "when", "timing", "optimize", "create"]
        recommendation_keywords = ["recommend", "suggest", "what should", "where should", "best", "top", "prefer", "like"]
        
        # Check for keywords
        for keyword in booking_keywords:
            if keyword in message_lower:
                return "booking"
        
        for keyword in itinerary_keywords:
            if keyword in message_lower:
                return "itinerary"
        
        for keyword in recommendation_keywords:
            if keyword in message_lower:
                return "recommendation"
        
        for keyword in search_keywords:
            if keyword in message_lower:
                return "search"
        
        # Default to search if unclear
        return "search"
    
    async def get_knowledge_context(self, user_message: str) -> Optional[str]:
        """Retrieve relevant knowledge context for the user message"""
        
        try:
            # Try to get relevant documents from knowledge base
            docs = await kb.query("destinations", user_message, n_results=2)
            
            if not docs:
                docs = await kb.query("tips", user_message, n_results=2)
            
            if docs:
                context_text = "\n".join([f"- {doc['content']}" for doc in docs])
                return context_text
        except Exception as e:
            print(f"Error retrieving knowledge context: {e}")
        
        return None
    
    async def handle_user_request(
        self,
        user_id: int,
        user_message: str,
        conversation_context: Optional[Dict] = None
    ) -> Dict:
        """
        Main entry point for handling user requests
        Routes to appropriate agent based on intent
        """
        
        # Classify intent
        intent = await self.classify_intent(user_message)
        
        # Get relevant knowledge context
        knowledge_context = await self.get_knowledge_context(user_message)
        
        # Get appropriate agent
        agent = self.agents.get(intent, self.search_agent)
        
        # Load user's conversation history with this agent
        try:
            await agent.load_conversation_history(user_id)
        except Exception as e:
            print(f"Could not load conversation history: {e}")
        
        # Process message with selected agent
        try:
            response = await agent.process_user_message(
                user_id=user_id,
                user_message=user_message,
                knowledge_context=knowledge_context
            )
            
            return {
                "status": "success",
                "agent": intent,
                "response": response,
                "timestamp": __import__("datetime").datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"Error processing request: {e}")
            return {
                "status": "error",
                "agent": intent,
                "response": f"I encountered an error: {str(e)}. Please try again.",
                "error": str(e)
            }
    
    async def handle_sequential_workflow(
        self,
        user_id: int,
        workflow: str,
        parameters: Dict
    ) -> Dict:
        """
        Handle multi-agent workflows that require sequential execution
        
        Workflows:
        - "search_and_plan": Search → Itinerary (find options and plan)
        - "search_and_book": Search → Booking (find and immediately book)
        - "full_trip": Search → Booking → Itinerary (complete trip planning and booking)
        """
        
        if workflow == "search_and_plan":
            # Step 1: Search for flights/hotels
            search_msg = f"Find {parameters.get('search_type', 'flights')} to {parameters.get('destination')} on {parameters.get('date')}"
            search_result = await self.handle_user_request(user_id, search_msg)
            
            # Step 2: Create itinerary
            itinerary_msg = f"Create an itinerary for my trip to {parameters.get('destination')}"
            itinerary_result = await self.handle_user_request(user_id, itinerary_msg)
            
            return {
                "workflow": workflow,
                "steps": [search_result, itinerary_result],
                "status": "completed"
            }
        
        elif workflow == "search_and_book":
            # Step 1: Search
            search_msg = parameters.get("search_message")
            search_result = await self.handle_user_request(user_id, search_msg)
            
            # Step 2: Book the selected option
            booking_msg = parameters.get("booking_message")
            booking_result = await self.handle_user_request(user_id, booking_msg)
            
            return {
                "workflow": workflow,
                "steps": [search_result, booking_result],
                "status": "completed"
            }
        
        elif workflow == "full_trip":
            # Step 1: Search
            search_msg = parameters.get("search_message")
            search_result = await self.handle_user_request(user_id, search_msg)
            
            # Step 2: Book
            booking_msg = parameters.get("booking_message")
            booking_result = await self.handle_user_request(user_id, booking_msg)
            
            # Step 3: Create itinerary
            itinerary_msg = parameters.get("itinerary_message")
            itinerary_result = await self.handle_user_request(user_id, itinerary_msg)
            
            return {
                "workflow": workflow,
                "steps": [search_result, booking_result, itinerary_result],
                "status": "completed"
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown workflow: {workflow}"
            }


# Global orchestrator instance
orchestrator = Orchestrator()
