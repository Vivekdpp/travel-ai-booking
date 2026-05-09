"""
Search Agent for TravelAI Booking System
Handles flight, hotel, and activity searches
"""

from typing import Dict, Optional
from src.agents.base_agent import BaseAgent
from src.tools.tools import FlightTools, HotelTools, ActivityTools
from src.embeddings import kb


class SearchAgent(BaseAgent):
    """Agent responsible for searching flights, hotels, and activities"""
    
    def __init__(self):
        super().__init__(
            agent_name="search_agent",
            agent_description="Searches for flights, hotels, and activities to help users find the best options"
        )
    
    def get_system_prompt(self) -> str:
        return """You are TravelAI's Search Agent. Your role is to help users find the best flights, hotels, and activities for their travels.

Key responsibilities:
1. Search for flights based on origin, destination, and dates
2. Search for hotels based on location, check-in/check-out dates, and preferences
3. Search for activities and attractions at destinations
4. Compare options and highlight the best choices based on price, ratings, and duration
5. Provide recommendations based on user budget and preferences

When a user asks to search or find travel options:
- Clarify any missing information (dates, number of passengers, preferences)
- Use the available search tools to find options
- Present results in a clear, organized way
- Highlight special deals or good value options
- Always inform the user about total costs when possible

Be conversational, helpful, and proactive in asking clarifying questions."""
    
    def get_tools(self) -> list:
        return [
            {
                "name": "search_flights",
                "description": "Search for available flights between two cities",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "3-letter airport code (e.g., YYC, YVR, JFK)"
                        },
                        "destination": {
                            "type": "string",
                            "description": "3-letter airport code (e.g., NYC, LAX, LDN)"
                        },
                        "departure_date": {
                            "type": "string",
                            "description": "Departure date in YYYY-MM-DD format"
                        },
                        "return_date": {
                            "type": "string",
                            "description": "Return date in YYYY-MM-DD format (optional for one-way flights)"
                        },
                        "passengers": {
                            "type": "integer",
                            "description": "Number of passengers",
                            "default": 1
                        }
                    },
                    "required": ["origin", "destination", "departure_date"]
                }
            },
            {
                "name": "search_hotels",
                "description": "Search for available hotels in a city",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "City name"
                        },
                        "check_in": {
                            "type": "string",
                            "description": "Check-in date in YYYY-MM-DD format"
                        },
                        "check_out": {
                            "type": "string",
                            "description": "Check-out date in YYYY-MM-DD format"
                        },
                        "budget": {
                            "type": "number",
                            "description": "Maximum budget per night in USD (optional)"
                        },
                        "amenities": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Desired amenities (e.g., 'WiFi', 'Pool', 'Gym')"
                        }
                    },
                    "required": ["city", "check_in", "check_out"]
                }
            },
            {
                "name": "search_activities",
                "description": "Search for activities and attractions at a destination",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "destination": {
                            "type": "string",
                            "description": "Destination city or location"
                        },
                        "category": {
                            "type": "string",
                            "description": "Activity category (e.g., 'tours', 'food', 'adventure', 'cultural')"
                        },
                        "date": {
                            "type": "string",
                            "description": "Activity date in YYYY-MM-DD format (optional)"
                        }
                    },
                    "required": ["destination"]
                }
            },
            {
                "name": "get_knowledge",
                "description": "Get travel knowledge, tips, and information about destinations",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "What you want to know (e.g., 'best time to visit Bangkok', 'budget travel tips')"
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, tool_input: Dict) -> Dict:
        """Execute search tools"""
        
        if tool_name == "search_flights":
            return await FlightTools.search_flights(
                origin=tool_input.get("origin"),
                destination=tool_input.get("destination"),
                departure_date=tool_input.get("departure_date"),
                return_date=tool_input.get("return_date"),
                passengers=tool_input.get("passengers", 1)
            )
        
        elif tool_name == "search_hotels":
            return await HotelTools.search_hotels(
                city=tool_input.get("city"),
                check_in=tool_input.get("check_in"),
                check_out=tool_input.get("check_out"),
                budget=tool_input.get("budget"),
                amenities=tool_input.get("amenities")
            )
        
        elif tool_name == "search_activities":
            return await ActivityTools.search_activities(
                destination=tool_input.get("destination"),
                category=tool_input.get("category"),
                date=tool_input.get("date")
            )
        
        elif tool_name == "get_knowledge":
            # Query knowledge base
            query = tool_input.get("query", "")
            docs = await kb.query("destinations", query, n_results=3)
            
            if not docs:
                docs = await kb.query("tips", query, n_results=3)
            
            if not docs:
                docs = await kb.query("activities", query, n_results=3)
            
            return {
                "status": "success",
                "query": query,
                "results": [doc["content"] for doc in docs] if docs else []
            }
        
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}
