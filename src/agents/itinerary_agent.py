"""
Itinerary Agent for TravelAI Booking System
Plans and optimizes travel schedules and itineraries
"""

from typing import Dict, List
from src.agents.base_agent import BaseAgent
from src.tools.tools import ItineraryTools
from src.embeddings import kb


class ItineraryAgent(BaseAgent):
    """Agent responsible for creating and optimizing travel itineraries"""
    
    def __init__(self):
        super().__init__(
            agent_name="itinerary_agent",
            agent_description="Plans, organizes, and optimizes travel itineraries and schedules"
        )
    
    def get_system_prompt(self) -> str:
        return """You are TravelAI's Itinerary Agent. Your role is to help users plan and optimize their travel schedules.

Key responsibilities:
1. Create comprehensive itineraries combining flights, hotels, and activities
2. Organize activities by date and location
3. Optimize schedules to minimize travel time
4. Identify and resolve scheduling conflicts
5. Provide daily breakdowns of activities and timings
6. Suggest timing for activities based on travel logistics
7. Generate printable/shareable itineraries

When creating an itinerary:
- Ask about must-see attractions and preferences
- Factor in travel time between locations
- Consider rest periods and meal times
- Suggest optimal ordering of activities
- Highlight any conflicts or issues
- Provide flexibility for adjustments

When optimizing:
- Minimize total travel time
- Group nearby activities together
- Consider opening hours and reservations
- Account for travel fatigue

Be creative, practical, and thoughtful about the user's travel experience."""
    
    def get_tools(self) -> list:
        return [
            {
                "name": "create_itinerary",
                "description": "Create a new travel itinerary",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "trip_name": {
                            "type": "string",
                            "description": "Name of the trip (e.g., 'Summer Europe Tour')"
                        },
                        "start_date": {
                            "type": "string",
                            "description": "Trip start date in YYYY-MM-DD format"
                        },
                        "end_date": {
                            "type": "string",
                            "description": "Trip end date in YYYY-MM-DD format"
                        },
                        "activities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "date": {"type": "string"},
                                    "time": {"type": "string"},
                                    "location": {"type": "string"},
                                    "duration_hours": {"type": "number"}
                                }
                            },
                            "description": "List of activities and their timings"
                        }
                    },
                    "required": ["trip_name", "start_date", "end_date", "activities"]
                }
            },
            {
                "name": "optimize_schedule",
                "description": "Optimize activity schedule to minimize travel time",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "activities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "date": {"type": "string"},
                                    "time": {"type": "string"},
                                    "location": {"type": "string"},
                                    "duration_hours": {"type": "number"}
                                }
                            },
                            "description": "List of activities to optimize"
                        }
                    },
                    "required": ["activities"]
                }
            },
            {
                "name": "get_travel_tips",
                "description": "Get travel tips and advice for destinations",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "What you want to know about travel"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, tool_input: Dict) -> Dict:
        """Execute itinerary tools"""
        
        if tool_name == "create_itinerary":
            return await ItineraryTools.create_itinerary(
                trip_name=tool_input.get("trip_name"),
                start_date=tool_input.get("start_date"),
                end_date=tool_input.get("end_date"),
                activities=tool_input.get("activities", [])
            )
        
        elif tool_name == "optimize_schedule":
            return await ItineraryTools.optimize_schedule(
                activities=tool_input.get("activities", [])
            )
        
        elif tool_name == "get_travel_tips":
            query = tool_input.get("query", "")
            docs = await kb.query("tips", query, n_results=3)
            
            if not docs:
                docs = await kb.query("destinations", query, n_results=3)
            
            return {
                "status": "success",
                "query": query,
                "tips": [doc["content"] for doc in docs] if docs else ["No tips found for this topic."]
            }
        
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}
