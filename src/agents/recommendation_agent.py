"""
Recommendation Agent for TravelAI Booking System
Provides personalized travel recommendations and suggestions
"""

from typing import Dict
from src.agents.base_agent import BaseAgent
from src.database import db
from src.embeddings import kb


class RecommendationAgent(BaseAgent):
    """Agent responsible for providing personalized travel recommendations"""
    
    def __init__(self):
        super().__init__(
            agent_name="recommendation_agent",
            agent_description="Provides personalized travel recommendations based on user preferences and history"
        )
    
    def get_system_prompt(self) -> str:
        return """You are TravelAI's Recommendation Agent. Your role is to provide personalized travel recommendations.

Key responsibilities:
1. Learn about user preferences (budget, travel style, interests)
2. Suggest destinations based on preferences and travel history
3. Recommend specific hotels based on past bookings
4. Suggest activities matching user interests
5. Provide local insights and travel tips
6. Identify trends in user travel patterns
7. Offer hidden gem recommendations

When recommending:
- Ask about budget constraints
- Understand travel style (luxury, budget, adventure, relaxation, cultural)
- Consider travel season and best time to visit
- Factor in past booking patterns
- Provide variety in recommendations
- Explain why each recommendation fits their profile

Recommendations should:
- Be data-informed (use past behavior)
- Include budget and timing information
- Have clear value propositions
- Address stated and implied interests
- Include alternatives at different price points

Be enthusiastic, personalized, and helpful."""
    
    def get_tools(self) -> list:
        return [
            {
                "name": "get_user_preferences",
                "description": "Get user's travel preferences and history",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "integer",
                            "description": "User ID"
                        }
                    },
                    "required": ["user_id"]
                }
            },
            {
                "name": "suggest_destinations",
                "description": "Suggest destinations based on preferences",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "budget": {
                            "type": "string",
                            "enum": ["budget", "mid-range", "luxury"],
                            "description": "Budget level"
                        },
                        "travel_style": {
                            "type": "string",
                            "enum": ["adventure", "relaxation", "cultural", "food", "beach", "city"],
                            "description": "Type of travel"
                        },
                        "duration_days": {
                            "type": "integer",
                            "description": "Trip duration in days"
                        }
                    },
                    "required": ["budget", "travel_style"]
                }
            },
            {
                "name": "get_destination_info",
                "description": "Get detailed information about a destination",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "destination": {
                            "type": "string",
                            "description": "Destination name"
                        }
                    },
                    "required": ["destination"]
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, tool_input: Dict) -> Dict:
        """Execute recommendation tools"""
        
        if tool_name == "get_user_preferences":
            user_id = tool_input.get("user_id")
            user = await db.get_user(user_id)
            
            if user:
                return {
                    "status": "success",
                    "user_id": user_id,
                    "name": user.get("name"),
                    "preferences": user.get("preferences", {}),
                    "member_since": user.get("created_at")
                }
            else:
                return {"status": "error", "message": "User not found"}
        
        elif tool_name == "suggest_destinations":
            budget = tool_input.get("budget")
            travel_style = tool_input.get("travel_style")
            
            # Query knowledge base for destination recommendations
            query = f"{travel_style} {budget} destinations"
            docs = await kb.query("destinations", query, n_results=5)
            
            destinations = [doc["content"] for doc in docs] if docs else []
            
            return {
                "status": "success",
                "budget": budget,
                "travel_style": travel_style,
                "suggested_destinations": destinations if destinations else [
                    f"Based on your {budget} budget and {travel_style} travel style, we recommend exploring our destination guides.",
                ]
            }
        
        elif tool_name == "get_destination_info":
            destination = tool_input.get("destination")
            
            # Query knowledge base
            docs = await kb.query("destinations", destination, n_results=3)
            tips = await kb.query("tips", destination, n_results=2)
            activities = await kb.query("activities", destination, n_results=3)
            hotels = await kb.query("hotels", destination, n_results=2)
            
            return {
                "status": "success",
                "destination": destination,
                "overview": docs[0]["content"] if docs else "Destination information not available",
                "tips": [doc["content"] for doc in tips] if tips else [],
                "activities": [doc["content"] for doc in activities] if activities else [],
                "hotels": [doc["content"] for doc in hotels] if hotels else []
            }
        
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}
