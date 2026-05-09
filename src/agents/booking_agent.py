"""
Booking Agent for TravelAI Booking System
Handles flight and hotel bookings, payments, and confirmations
"""

from typing import Dict
from src.agents.base_agent import BaseAgent
from src.tools.tools import FlightTools, HotelTools, BookingTools, ActivityTools


class BookingAgent(BaseAgent):
    """Agent responsible for processing bookings and payments"""
    
    def __init__(self):
        super().__init__(
            agent_name="booking_agent",
            agent_description="Handles flight, hotel, and activity bookings, payments, and confirmations"
        )
    
    def get_system_prompt(self) -> str:
        return """You are TravelAI's Booking Agent. Your role is to help users complete their travel bookings and process payments.

Key responsibilities:
1. Confirm flight, hotel, and activity bookings
2. Collect necessary passenger/guest information
3. Process payments securely
4. Generate confirmation numbers and booking details
5. Handle cancellations and modifications
6. Provide booking summaries and next steps

When a user wants to book:
- Confirm all booking details (dates, room type, number of guests, etc.)
- Verify passenger names and contact information
- Confirm the total cost
- Process payment using the payment tool
- Provide a clear confirmation with reference number

Always:
- Double-check information before processing
- Explain payment terms and cancellation policies
- Provide booking confirmation details
- Offer assistance with any follow-up questions

Be professional, thorough, and reassuring."""
    
    def get_tools(self) -> list:
        return [
            {
                "name": "get_flight_details",
                "description": "Get detailed information about a specific flight",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "flight_id": {
                            "type": "string",
                            "description": "Flight ID (e.g., FL12345)"
                        }
                    },
                    "required": ["flight_id"]
                }
            },
            {
                "name": "book_flight",
                "description": "Book a flight for passengers",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "flight_id": {
                            "type": "string",
                            "description": "Flight ID to book"
                        },
                        "passenger_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of passenger names"
                        }
                    },
                    "required": ["flight_id", "passenger_names"]
                }
            },
            {
                "name": "get_hotel_details",
                "description": "Get detailed information about a specific hotel",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "hotel_id": {
                            "type": "string",
                            "description": "Hotel ID"
                        }
                    },
                    "required": ["hotel_id"]
                }
            },
            {
                "name": "book_hotel",
                "description": "Book a hotel room",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "hotel_id": {
                            "type": "string",
                            "description": "Hotel ID to book"
                        },
                        "check_in": {
                            "type": "string",
                            "description": "Check-in date in YYYY-MM-DD format"
                        },
                        "check_out": {
                            "type": "string",
                            "description": "Check-out date in YYYY-MM-DD format"
                        },
                        "room_type": {
                            "type": "string",
                            "description": "Room type (e.g., 'standard', 'deluxe', 'suite')"
                        },
                        "guest_name": {
                            "type": "string",
                            "description": "Guest name for the reservation"
                        }
                    },
                    "required": ["hotel_id", "check_in", "check_out", "room_type", "guest_name"]
                }
            },
            {
                "name": "book_activity",
                "description": "Book an activity or tour",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "activity_id": {
                            "type": "string",
                            "description": "Activity ID"
                        },
                        "date": {
                            "type": "string",
                            "description": "Activity date in YYYY-MM-DD format"
                        },
                        "num_people": {
                            "type": "integer",
                            "description": "Number of people"
                        },
                        "guest_name": {
                            "type": "string",
                            "description": "Primary guest name"
                        }
                    },
                    "required": ["activity_id", "date", "num_people", "guest_name"]
                }
            },
            {
                "name": "process_payment",
                "description": "Process payment for bookings",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "amount": {
                            "type": "number",
                            "description": "Amount to charge in USD"
                        },
                        "currency": {
                            "type": "string",
                            "description": "Currency code (default: USD)",
                            "default": "USD"
                        },
                        "payment_method": {
                            "type": "string",
                            "description": "Payment method (credit_card, debit_card, etc.)",
                            "default": "credit_card"
                        }
                    },
                    "required": ["amount"]
                }
            },
            {
                "name": "calculate_total_cost",
                "description": "Calculate total cost of bookings",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "price": {"type": "number"},
                                    "quantity": {"type": "integer"}
                                }
                            },
                            "description": "List of items with price and quantity"
                        }
                    },
                    "required": ["items"]
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, tool_input: Dict) -> Dict:
        """Execute booking tools"""
        
        if tool_name == "get_flight_details":
            return await FlightTools.get_flight_details(
                flight_id=tool_input.get("flight_id")
            )
        
        elif tool_name == "book_flight":
            return await FlightTools.book_flight(
                flight_id=tool_input.get("flight_id"),
                passenger_names=tool_input.get("passenger_names", [])
            )
        
        elif tool_name == "get_hotel_details":
            return await HotelTools.get_hotel_details(
                hotel_id=tool_input.get("hotel_id")
            )
        
        elif tool_name == "book_hotel":
            return await HotelTools.book_hotel(
                hotel_id=tool_input.get("hotel_id"),
                check_in=tool_input.get("check_in"),
                check_out=tool_input.get("check_out"),
                room_type=tool_input.get("room_type"),
                guest_name=tool_input.get("guest_name")
            )
        
        elif tool_name == "book_activity":
            return await ActivityTools.book_activity(
                activity_id=tool_input.get("activity_id"),
                date=tool_input.get("date"),
                num_people=tool_input.get("num_people"),
                guest_name=tool_input.get("guest_name")
            )
        
        elif tool_name == "process_payment":
            return await BookingTools.process_payment(
                amount=tool_input.get("amount"),
                currency=tool_input.get("currency", "USD"),
                payment_method=tool_input.get("payment_method", "credit_card")
            )
        
        elif tool_name == "calculate_total_cost":
            return await BookingTools.get_total_cost(
                items=tool_input.get("items", [])
            )
        
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}
