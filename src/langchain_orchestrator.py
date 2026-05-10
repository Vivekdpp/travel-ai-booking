"""
LangChain/LangGraph Multi-Agent Orchestrator
TravelAI Booking System - Compatible with LangChain v1.x

This file demonstrates the SAME functionality as our custom framework
but using LangChain + LangGraph industry-standard libraries.

Comparison:
  Custom approach:    orchestrator.py + base_agent.py = ~300 lines
  LangChain approach: this file = ~200 lines

Architecture:
  LangGraph StateGraph = our orchestrator.py
  Claude with tools    = our base_agent.py tool calling loop
  @tool decorator      = our tools.py functions
  ChatAnthropic        = our Anthropic client
"""

import os
import asyncio
import json
import concurrent.futures
from typing import TypedDict, Literal
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LangChain imports (v1.x compatible)
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

# LangGraph imports
from langgraph.graph import StateGraph, END

# Our existing tools (reuse same logic!)
from src.tools.tools import (
    FlightTools,
    HotelTools,
    ActivityTools,
    BookingTools,
    ItineraryTools
)


# ============================================================
# HELPER: Run async functions in sync context
# ============================================================

def run_sync(coro):
    """
    Run async function synchronously using ThreadPoolExecutor.
    
    Why needed?
    LangChain tools run synchronously but our tools are async.
    This bridges the gap safely without conflicting with uvicorn.
    """
    with concurrent.futures.ThreadPoolExecutor() as pool:
        future = pool.submit(asyncio.run, coro)
        return future.result()


# ============================================================
# STEP 1: DEFINE STATE
# ============================================================

class TravelState(TypedDict):
    """
    State that flows through the LangGraph.
    Like a shared notepad all agents can read/write.
    
    Our custom equivalent:
    The response dict passed between agents
    """
    user_message: str
    user_id: int
    intent: str
    response: str
    agent_used: str


# ============================================================
# STEP 2: DEFINE TOOLS WITH @tool DECORATOR
# ============================================================

@tool
def search_flights(origin: str, destination: str, departure_date: str) -> str:
    """
    Search for available flights between two cities.
    Use when user wants to find flights or search for air travel.

    Args:
        origin: 3-letter airport code (YYZ, JFK, LAX)
        destination: 3-letter airport code
        departure_date: Date in YYYY-MM-DD format
    """
    result = run_sync(
        FlightTools.search_flights(origin, destination, departure_date)
    )
    return json.dumps(result)


@tool
def search_hotels(city: str, check_in: str, check_out: str) -> str:
    """
    Search for available hotels in a city.
    Use when user wants to find hotels or accommodation.

    Args:
        city: City name (New York, Toronto, Paris)
        check_in: Check-in date in YYYY-MM-DD format
        check_out: Check-out date in YYYY-MM-DD format
    """
    result = run_sync(
        HotelTools.search_hotels(city, check_in, check_out)
    )
    return json.dumps(result)


@tool
def search_activities(destination: str, category: str = "general") -> str:
    """
    Search for activities and attractions at a destination.
    Use when user asks about things to do or local activities.

    Args:
        destination: City or location name
        category: Activity type (tours, food, adventure, cultural)
    """
    result = run_sync(
        ActivityTools.search_activities(destination, category)
    )
    return json.dumps(result)


@tool
def book_flight(flight_id: str, passenger_name: str) -> str:
    """
    Book a flight for a passenger.
    Use when user wants to confirm and book a specific flight.

    Args:
        flight_id: Flight ID from search results (e.g., FL12345)
        passenger_name: Full name of passenger
    """
    result = run_sync(
        FlightTools.book_flight(flight_id, [passenger_name])
    )
    return json.dumps(result)


@tool
def book_hotel(
    hotel_id: str,
    check_in: str,
    check_out: str,
    guest_name: str
) -> str:
    """
    Book a hotel room for a guest.
    Use when user wants to reserve a specific hotel.

    Args:
        hotel_id: Hotel ID from search results
        check_in: Check-in date YYYY-MM-DD
        check_out: Check-out date YYYY-MM-DD
        guest_name: Full name of guest
    """
    result = run_sync(
        HotelTools.book_hotel(
            hotel_id, check_in, check_out, "standard", guest_name
        )
    )
    return json.dumps(result)


@tool
def process_payment(amount: float) -> str:
    """
    Process payment for a booking.
    Use when user confirms and wants to pay for booking.

    Args:
        amount: Total amount to charge in USD
    """
    result = run_sync(
        BookingTools.process_payment(amount)
    )
    return json.dumps(result)


@tool
def create_trip_itinerary(
    trip_name: str,
    start_date: str,
    end_date: str
) -> str:
    """
    Create a travel itinerary for a trip.
    Use when user wants to plan or organize their trip schedule.

    Args:
        trip_name: Name of the trip (e.g., NYC Adventure)
        start_date: Trip start date YYYY-MM-DD
        end_date: Trip end date YYYY-MM-DD
    """
    result = run_sync(
        ItineraryTools.create_itinerary(
            trip_name=trip_name,
            start_date=start_date,
            end_date=end_date,
            activities=[]
        )
    )
    return json.dumps(result)


@tool
def get_destination_recommendations(
    budget: str,
    travel_style: str
) -> str:
    """
    Get personalized destination recommendations.
    Use when user asks where to go or wants travel suggestions.

    Args:
        budget: Budget level (budget, mid-range, luxury)
        travel_style: Type (beach, adventure, cultural, city, relaxation)
    """
    recommendations = {
        "budget": {
            "beach": ["Bali", "Cancun", "Phuket"],
            "adventure": ["Nepal", "Peru", "Vietnam"],
            "city": ["Bangkok", "Budapest", "Lisbon"],
            "relaxation": ["Goa", "Koh Samui", "Zanzibar"],
            "cultural": ["Morocco", "Cambodia", "Bolivia"]
        },
        "mid-range": {
            "beach": ["Maldives", "Santorini", "Turks & Caicos"],
            "adventure": ["New Zealand", "Iceland", "Patagonia"],
            "city": ["Barcelona", "Singapore", "New York"],
            "relaxation": ["Bora Bora", "Costa Rica", "Tuscany"],
            "cultural": ["Japan", "Italy", "Portugal"]
        },
        "luxury": {
            "beach": ["Maldives Private Villa", "Seychelles", "Fiji"],
            "adventure": ["Antarctic Expedition", "Galapagos", "Safari Kenya"],
            "city": ["Monaco", "Dubai", "Paris"],
            "relaxation": ["Bali Private Villa", "St. Barts", "Tahiti"],
            "cultural": ["Kyoto Private Tours", "Amalfi Coast", "Swiss Alps"]
        }
    }

    budget_key = budget.lower() if budget.lower() in recommendations else "mid-range"
    style_key = (
        travel_style.lower()
        if travel_style.lower() in recommendations[budget_key]
        else "city"
    )

    suggested = recommendations[budget_key][style_key]
    result = {
        "status": "success",
        "budget": budget,
        "travel_style": travel_style,
        "recommendations": suggested,
        "message": f"Top destinations: {', '.join(suggested)}"
    }
    return json.dumps(result)


@tool
def get_travel_tips(destination: str) -> str:
    """
    Get travel tips and local insights for a destination.
    Use when user wants advice about a specific place.

    Args:
        destination: Destination city or country
    """
    result = {
        "status": "success",
        "destination": destination,
        "tips": [
            "Book flights 2-3 months in advance",
            "Always get travel insurance",
            "Keep copies of important documents",
            "Learn basic local phrases",
            "Notify your bank before traveling"
        ],
        "currency_tip": "Use ATMs for best exchange rates",
        "transport_tip": "Research local transportation options"
    }
    return json.dumps(result)


# ============================================================
# STEP 3: CREATE LLM
# ============================================================

llm = ChatAnthropic(
    model="claude-sonnet-4-5",
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
)


# ============================================================
# STEP 4: AGENT RUNNER FUNCTION
# Uses LangChain bind_tools (modern approach)
# ============================================================

def run_agent_with_tools(
    system_prompt: str,
    tools: list,
    user_message: str
) -> str:
    """
    Run an agent with tools using LangChain v1.x bind_tools.

    This is the tool calling loop.
    Our custom equivalent: base_agent.py process_user_message()

    LangChain approach:
    1. Bind tools to LLM
    2. Call LLM with messages
    3. If tool_calls → execute tools → loop
    4. If no tool_calls → return response
    """

    # Bind tools to LLM (tells Claude what tools are available)
    llm_with_tools = llm.bind_tools(tools)

    # Build tool lookup map for fast access
    tool_map = {t.name: t for t in tools}

    # Initial messages
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    # Tool calling loop
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Call Claude
        response = llm_with_tools.invoke(messages)

        # Check if Claude wants to use tools
        if hasattr(response, 'tool_calls') and response.tool_calls:

            # Add Claude's response to messages
            messages.append(response)

            # Execute each tool
            for tool_call in response.tool_calls:
                tool_name = tool_call['name']
                tool_args = tool_call['args']
                tool_id = tool_call['id']

                # Execute the tool
                try:
                    if tool_name in tool_map:
                        tool_result = tool_map[tool_name].invoke(tool_args)
                    else:
                        tool_result = f"Tool {tool_name} not found"
                except Exception as e:
                    tool_result = f"Tool error: {str(e)}"

                # Add tool result to messages
                messages.append(
                    ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_id
                    )
                )

        else:
            # Claude is done - return final response
            return response.content

    return "Request processed."


# ============================================================
# STEP 5: LANGGRAPH NODES AND ROUTING
# ============================================================

def classify_intent(message: str) -> str:
    """Classify user intent - same as orchestrator.py"""
    message_lower = message.lower()

    booking_keywords = ["book", "reserve", "confirm", "pay", "checkout"]
    itinerary_keywords = ["plan", "itinerary", "schedule", "organize", "create"]
    recommendation_keywords = ["recommend", "suggest", "where should", "best", "top"]
    search_keywords = ["search", "find", "show", "flights", "hotels", "available"]

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

    return "search"


def router_node(state: TravelState) -> TravelState:
    """Router node - classifies intent and routes to right agent"""
    intent = classify_intent(state["user_message"])
    return {**state, "intent": intent}


def search_node(state: TravelState) -> TravelState:
    """Search Agent - finds flights, hotels, activities"""
    response = run_agent_with_tools(
        system_prompt="""You are TravelAI's Search Agent.
        Find flights, hotels, and activities for users.
        Always use tools to get real data.
        Present results clearly with prices and details.
        Highlight the best value options.""",
        tools=[search_flights, search_hotels, search_activities],
        user_message=state["user_message"]
    )
    return {**state, "response": response, "agent_used": "search"}


def booking_node(state: TravelState) -> TravelState:
    """Booking Agent - handles reservations and payments"""
    response = run_agent_with_tools(
        system_prompt="""You are TravelAI's Booking Agent.
        Handle reservations and payments.
        Always confirm details before processing.
        Provide confirmation numbers after booking.""",
        tools=[book_flight, book_hotel, process_payment],
        user_message=state["user_message"]
    )
    return {**state, "response": response, "agent_used": "booking"}


def itinerary_node(state: TravelState) -> TravelState:
    """Itinerary Agent - plans and optimizes schedules"""
    response = run_agent_with_tools(
        system_prompt="""You are TravelAI's Itinerary Agent.
        Plan and optimize travel schedules.
        Create detailed day-by-day itineraries.
        Consider travel time between locations.""",
        tools=[create_trip_itinerary],
        user_message=state["user_message"]
    )
    return {**state, "response": response, "agent_used": "itinerary"}


def recommendation_node(state: TravelState) -> TravelState:
    """Recommendation Agent - personalized suggestions"""
    response = run_agent_with_tools(
        system_prompt="""You are TravelAI's Recommendation Agent.
        Provide personalized travel suggestions.
        Ask about budget and travel style if not provided.
        Explain why each destination suits the user.""",
        tools=[get_destination_recommendations, get_travel_tips],
        user_message=state["user_message"]
    )
    return {**state, "response": response, "agent_used": "recommendation"}


def route_to_agent(
    state: TravelState
) -> Literal["search", "booking", "itinerary", "recommendation"]:
    """Routing function for conditional edges"""
    return state["intent"]


# ============================================================
# STEP 6: BUILD LANGGRAPH
# ============================================================

def build_travel_graph():
    """
    Build and compile the LangGraph StateGraph.

    Flow:
    START → router → [search|booking|itinerary|recommendation] → END

    Our custom equivalent:
    orchestrator.py → handle_user_request()
    """
    graph = StateGraph(TravelState)

    # Add nodes (agents)
    graph.add_node("router", router_node)
    graph.add_node("search", search_node)
    graph.add_node("booking", booking_node)
    graph.add_node("itinerary", itinerary_node)
    graph.add_node("recommendation", recommendation_node)

    # Entry point
    graph.set_entry_point("router")

    # Conditional routing based on intent
    graph.add_conditional_edges(
        "router",
        route_to_agent,
        {
            "search": "search",
            "booking": "booking",
            "itinerary": "itinerary",
            "recommendation": "recommendation"
        }
    )

    # All agents end after responding
    graph.add_edge("search", END)
    graph.add_edge("booking", END)
    graph.add_edge("itinerary", END)
    graph.add_edge("recommendation", END)

    return graph.compile()


# Compile graph once at startup
travel_app = build_travel_graph()


# ============================================================
# STEP 7: ORCHESTRATOR CLASS
# Same interface as our custom Orchestrator!
# ============================================================

class LangChainOrchestrator:
    """
    LangChain + LangGraph version of our Orchestrator.

    Same interface as orchestrator.py:
    Both have handle_user_request(user_id, user_message)

    This means we can swap between them easily!
    Same interface, different implementation.
    That's good software design! (Interface Segregation)
    """

    def __init__(self):
        self.graph = travel_app
        print("✓ LangGraph travel graph initialized")

    async def handle_user_request(
        self,
        user_id: int,
        user_message: str
    ) -> dict:
        """
        Handle user request using LangGraph.

        Flow:
        1. Create initial state
        2. LangGraph routes to correct agent
        3. Agent uses tools via LangChain
        4. Returns response

        Our custom equivalent:
        orchestrator.handle_user_request()
        """
        try:
            # Create initial state
            initial_state = TravelState(
                user_message=user_message,
                user_id=user_id,
                intent="",
                response="",
                agent_used=""
            )

            # Run through LangGraph
            # This handles: routing → agent → tools → response
            final_state = self.graph.invoke(initial_state)

            return {
                "status": "success",
                "agent": final_state["agent_used"],
                "response": final_state["response"],
                "framework": "LangChain + LangGraph",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"LangGraph error: {e}")
            return {
                "status": "error",
                "agent": "langchain",
                "response": f"I encountered an error: {str(e)}",
                "framework": "LangChain + LangGraph",
                "timestamp": datetime.now().isoformat()
            }


# Global instance (same pattern as our custom orchestrator)
langchain_orchestrator = LangChainOrchestrator()