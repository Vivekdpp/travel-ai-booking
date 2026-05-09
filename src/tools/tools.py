"""
Tool implementations for TravelAI Booking System
Includes flight, hotel, booking, and activity tools
"""

import json
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class FlightTools:
    """Flight search and booking tools"""
    
    @staticmethod
    async def search_flights(
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        passengers: int = 1
    ) -> Dict:
        """Search for available flights"""
        
        # Simulate flight search delay
        await asyncio.sleep(0.5)
        
        airlines = ['United', 'American', 'Delta', 'Southwest', 'Air Canada']
        prices = [200, 350, 450, 550, 750]
        
        flights = []
        for i in range(5):
            departure = f"{departure_date}T{8 + i*2:02d}:00:00Z"
            arrival_time = 5 + i  # hours of flight
            arrival = datetime.fromisoformat(departure_date.replace('-', '') + "T000000").isoformat() + "Z"
            
            flights.append({
                "flight_id": f"FL{random.randint(10000, 99999)}",
                "airline": airlines[i],
                "departure": departure,
                "arrival": arrival,
                "duration_hours": arrival_time,
                "stops": 0 if i < 3 else 1,
                "price": prices[i],
                "currency": "USD"
            })
        
        return {
            "status": "success",
            "route": f"{origin} -> {destination}",
            "departure_date": departure_date,
            "passengers": passengers,
            "total_flights": len(flights),
            "flights": flights
        }
    
    @staticmethod
    async def get_flight_details(flight_id: str) -> Dict:
        """Get detailed information about a flight"""
        
        await asyncio.sleep(0.3)
        
        return {
            "flight_id": flight_id,
            "airline": "United Airlines",
            "aircraft": "Boeing 777",
            "baggage_allowance": {
                "carry_on": "1 bag + 1 personal item",
                "checked": "2 bags free"
            },
            "seat_options": ["Economy", "Premium Economy", "Business"],
            "meals": "Free meal included",
            "amenities": ["WiFi", "Entertainment System", "Blanket & Pillow"]
        }
    
    @staticmethod
    async def book_flight(flight_id: str, passenger_names: List[str]) -> Dict:
        """Book a flight"""
        
        await asyncio.sleep(1)
        
        confirmation_number = f"CONF{random.randint(100000, 999999)}"
        
        return {
            "status": "booked",
            "confirmation_number": confirmation_number,
            "flight_id": flight_id,
            "passengers": passenger_names,
            "booking_reference": f"BR{random.randint(10000, 99999)}",
            "booking_time": datetime.now().isoformat(),
            "message": f"Flight booked successfully. Confirmation: {confirmation_number}"
        }


class HotelTools:
    """Hotel search and booking tools"""
    
    @staticmethod
    async def search_hotels(
        city: str,
        check_in: str,
        check_out: str,
        budget: Optional[float] = None,
        amenities: Optional[List[str]] = None
    ) -> Dict:
        """Search for available hotels"""
        
        await asyncio.sleep(0.5)
        
        hotels = [
            {
                "hotel_id": "H001",
                "name": f"Luxury {city} Hotel",
                "stars": 5,
                "price_per_night": 300,
                "location": f"Downtown {city}",
                "amenities": ["WiFi", "Pool", "Spa", "Restaurant"],
                "rating": 4.8,
                "available_rooms": 10
            },
            {
                "hotel_id": "H002",
                "name": f"Budget {city} Inn",
                "stars": 3,
                "price_per_night": 80,
                "location": f"Mid {city}",
                "amenities": ["WiFi", "Gym"],
                "rating": 4.2,
                "available_rooms": 25
            },
            {
                "hotel_id": "H003",
                "name": f"Business {city} Hotel",
                "stars": 4,
                "price_per_night": 150,
                "location": f"Business District {city}",
                "amenities": ["WiFi", "Meeting Rooms", "Gym", "Restaurant"],
                "rating": 4.5,
                "available_rooms": 15
            },
        ]
        
        return {
            "status": "success",
            "city": city,
            "check_in": check_in,
            "check_out": check_out,
            "total_hotels": len(hotels),
            "hotels": hotels
        }
    
    @staticmethod
    async def get_hotel_details(hotel_id: str) -> Dict:
        """Get detailed information about a hotel"""
        
        await asyncio.sleep(0.3)
        
        return {
            "hotel_id": hotel_id,
            "name": "Luxury Hotel",
            "description": "5-star luxury hotel with world-class service",
            "amenities": {
                "room": ["AC", "WiFi", "Smart TV", "Mini Bar", "Safe"],
                "property": ["Pool", "Spa", "Restaurant", "Bar", "Gym"]
            },
            "room_types": {
                "standard": {"price": 250, "beds": 1},
                "deluxe": {"price": 350, "beds": 1},
                "suite": {"price": 600, "beds": 2}
            },
            "policies": {
                "check_in": "3:00 PM",
                "check_out": "11:00 AM",
                "cancellation": "Free cancellation up to 24 hours before arrival"
            }
        }
    
    @staticmethod
    async def book_hotel(hotel_id: str, check_in: str, check_out: str, room_type: str, guest_name: str) -> Dict:
        """Book a hotel"""
        
        await asyncio.sleep(1)
        
        booking_reference = f"BH{random.randint(100000, 999999)}"
        
        return {
            "status": "booked",
            "hotel_id": hotel_id,
            "booking_reference": booking_reference,
            "guest_name": guest_name,
            "check_in": check_in,
            "check_out": check_out,
            "room_type": room_type,
            "booking_time": datetime.now().isoformat(),
            "message": f"Hotel booked successfully. Reference: {booking_reference}"
        }


class ActivityTools:
    """Activity and attraction search tools"""
    
    @staticmethod
    async def search_activities(
        destination: str,
        category: Optional[str] = None,
        date: Optional[str] = None
    ) -> Dict:
        """Search for activities and attractions"""
        
        await asyncio.sleep(0.4)
        
        activities = [
            {
                "activity_id": "A001",
                "name": f"City Tour of {destination}",
                "category": "tours",
                "price": 50,
                "duration_hours": 4,
                "rating": 4.7,
                "description": f"Guided tour of major attractions in {destination}"
            },
            {
                "activity_id": "A002",
                "name": f"Local Food Tour in {destination}",
                "category": "food",
                "price": 75,
                "duration_hours": 3,
                "rating": 4.8,
                "description": f"Taste authentic cuisine in {destination}"
            },
            {
                "activity_id": "A003",
                "name": f"Adventure Activity in {destination}",
                "category": "adventure",
                "price": 120,
                "duration_hours": 5,
                "rating": 4.5,
                "description": f"Exciting outdoor adventure in {destination}"
            },
        ]
        
        return {
            "status": "success",
            "destination": destination,
            "category": category,
            "total_activities": len(activities),
            "activities": activities
        }
    
    @staticmethod
    async def book_activity(activity_id: str, date: str, num_people: int, guest_name: str) -> Dict:
        """Book an activity"""
        
        await asyncio.sleep(0.8)
        
        booking_ref = f"BA{random.randint(100000, 999999)}"
        
        return {
            "status": "booked",
            "activity_id": activity_id,
            "booking_reference": booking_ref,
            "guest_name": guest_name,
            "date": date,
            "num_people": num_people,
            "message": f"Activity booked successfully. Reference: {booking_ref}"
        }


class BookingTools:
    """Payment and booking confirmation tools"""
    
    @staticmethod
    async def process_payment(amount: float, currency: str = "USD", payment_method: str = "credit_card") -> Dict:
        """Process payment"""
        
        await asyncio.sleep(2)  # Simulate payment processing
        
        transaction_id = f"TXN{random.randint(100000, 999999)}"
        
        return {
            "status": "success",
            "transaction_id": transaction_id,
            "amount": amount,
            "currency": currency,
            "payment_method": payment_method,
            "timestamp": datetime.now().isoformat(),
            "message": f"Payment processed successfully. Transaction ID: {transaction_id}"
        }
    
    @staticmethod
    async def get_total_cost(items: List[Dict]) -> Dict:
        """Calculate total cost of bookings"""
        
        total = sum(item.get('price', 0) * item.get('quantity', 1) for item in items)
        
        return {
            "status": "success",
            "items": items,
            "subtotal": total,
            "tax": round(total * 0.1, 2),
            "total": round(total * 1.1, 2),
            "currency": "USD"
        }


class ItineraryTools:
    """Itinerary planning and optimization tools"""
    
    @staticmethod
    async def create_itinerary(trip_name: str, start_date: str, end_date: str, activities: List[Dict]) -> Dict:
        """Create an itinerary"""
        
        await asyncio.sleep(0.5)
        
        itinerary_id = f"IT{random.randint(100000, 999999)}"
        
        return {
            "status": "created",
            "itinerary_id": itinerary_id,
            "trip_name": trip_name,
            "start_date": start_date,
            "end_date": end_date,
            "num_activities": len(activities),
            "message": f"Itinerary created successfully. ID: {itinerary_id}"
        }
    
    @staticmethod
    async def optimize_schedule(activities: List[Dict]) -> Dict:
        """Optimize activity schedule to minimize travel time"""
        
        await asyncio.sleep(1)
        
        # Simple optimization: sort by time
        optimized = sorted(activities, key=lambda x: x.get('time', ''))
        
        return {
            "status": "optimized",
            "original_activities": len(activities),
            "optimized_activities": optimized,
            "time_saved_hours": 2,
            "message": "Schedule optimized to minimize travel time"
        }
