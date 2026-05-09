"""
Embeddings and Vector DB module for TravelAI Booking System
Uses Chroma for semantic search over travel knowledge
"""

import chromadb
import json
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from src.config import settings


class KnowledgeBase:
    """Vector database for travel knowledge and context"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_path)
        self.collections = {}
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self._initialize_collections()
    
    def _initialize_collections(self):
        """Initialize Chroma collections"""
        self.collections['destinations'] = self.client.get_or_create_collection(
            name="travel_destinations",
            metadata={"description": "Popular travel destinations and guides"}
        )
        self.collections['hotels'] = self.client.get_or_create_collection(
            name="hotel_database",
            metadata={"description": "Hotel information and reviews"}
        )
        self.collections['activities'] = self.client.get_or_create_collection(
            name="activities",
            metadata={"description": "Activities and attractions"}
        )
        self.collections['tips'] = self.client.get_or_create_collection(
            name="travel_tips",
            metadata={"description": "Travel tips and local insights"}
        )
        print(f"✓ Vector DB initialized with {len(self.collections)} collections")
    
    async def query(self, collection_name: str, query_text: str, n_results: int = 5) -> List[Dict]:
        """Query knowledge base for relevant documents"""
        if collection_name not in self.collections:
            return []
        
        collection = self.collections[collection_name]
        results = collection.query(
            query_texts=[query_text],
            n_results=min(n_results, 5)
        )
        
        # Format results
        documents = []
        if results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                documents.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })
        
        return documents
    
    async def add_documents(self, collection_name: str, documents: List[Dict]):
        """Add documents to knowledge base"""
        if collection_name not in self.collections:
            return
        
        collection = self.collections[collection_name]
        
        # Prepare documents
        ids = [doc.get('id', f"{collection_name}_{i}") for i, doc in enumerate(documents)]
        texts = [doc['content'] for doc in documents]
        metadatas = [doc.get('metadata', {}) for doc in documents]
        
        # Add to collection
        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
        
        print(f"✓ Added {len(documents)} documents to {collection_name}")
    
    async def seed_knowledge_base(self):
        """Initialize knowledge base with sample travel data"""
        
        # Popular destinations
        destinations = [
            {
                'id': 'dest_nyc',
                'content': 'New York City: A vibrant city known for iconic landmarks like the Statue of Liberty, Central Park, and Times Square. Best time to visit: September-November and March-May.',
                'metadata': {'type': 'destination', 'region': 'North America', 'budget': 'high'}
            },
            {
                'id': 'dest_bkk',
                'content': 'Bangkok, Thailand: Thailand\'s capital featuring ornate temples, bustling street food markets, and vibrant nightlife. Best time to visit: November-February (cool and dry season).',
                'metadata': {'type': 'destination', 'region': 'Asia', 'budget': 'low'}
            },
            {
                'id': 'dest_paris',
                'content': 'Paris, France: The City of Light known for the Eiffel Tower, museums, and world-class cuisine. Best time to visit: April-June and September-October.',
                'metadata': {'type': 'destination', 'region': 'Europe', 'budget': 'high'}
            },
            {
                'id': 'dest_tokyo',
                'content': 'Tokyo, Japan: A blend of ancient temples and cutting-edge technology. Features Senso-ji temple, shibuya crossing, and excellent public transportation. Best time: Spring (cherry blossoms) and Fall.',
                'metadata': {'type': 'destination', 'region': 'Asia', 'budget': 'medium'}
            },
            {
                'id': 'dest_bali',
                'content': 'Bali, Indonesia: A tropical paradise known for beautiful beaches, rice terraces, and Hindu temples. Perfect for relaxation and adventure. Budget-friendly with excellent resorts.',
                'metadata': {'type': 'destination', 'region': 'Asia', 'budget': 'low'}
            },
        ]
        
        # Travel tips
        tips = [
            {
                'id': 'tip_budget',
                'content': 'Budget Travel Tips: 1) Book flights 2-3 months in advance. 2) Travel during shoulder season for better deals. 3) Use public transportation. 4) Eat where locals eat. 5) Book accommodations in hostels or budget hotels.',
                'metadata': {'type': 'tip', 'category': 'budget', 'rating': 5}
            },
            {
                'id': 'tip_packing',
                'content': 'Smart Packing Essentials: 1) Universal power adapter. 2) Travel insurance documents. 3) Comfortable walking shoes. 4) Lightweight layers. 5) Portable phone charger. 6) Medications and basic first aid.',
                'metadata': {'type': 'tip', 'category': 'packing', 'rating': 5}
            },
            {
                'id': 'tip_safety',
                'content': 'Travel Safety Tips: 1) Share your itinerary with someone. 2) Register with your embassy. 3) Keep copies of important documents. 4) Avoid displaying expensive items. 5) Be aware of local laws and customs.',
                'metadata': {'type': 'tip', 'category': 'safety', 'rating': 5}
            },
            {
                'id': 'tip_jet_lag',
                'content': 'Managing Jet Lag: 1) Start adjusting sleep 3 days before travel. 2) Stay hydrated on flights. 3) Avoid alcohol and caffeine. 4) Get sunlight exposure at your destination. 5) Don\'t nap on arrival day if possible.',
                'metadata': {'type': 'tip', 'category': 'health', 'rating': 4}
            },
        ]
        
        # Hotels
        hotels = [
            {
                'id': 'hotel_nyc_plaza',
                'content': 'Plaza Hotel, New York: Luxury 5-star hotel on Fifth Avenue overlooking Central Park. Famous for afternoon tea service. Rooms from $800/night.',
                'metadata': {'type': 'hotel', 'city': 'New York', 'stars': 5, 'price_range': 'luxury'}
            },
            {
                'id': 'hotel_bkk_akyra',
                'content': 'Akyra Manor, Bangkok: Boutique 4-star hotel with contemporary design in Thonglor area. Great location near shopping and dining. Rooms from $100/night.',
                'metadata': {'type': 'hotel', 'city': 'Bangkok', 'stars': 4, 'price_range': 'mid-range'}
            },
        ]
        
        # Activities
        activities = [
            {
                'id': 'activity_statue_liberty',
                'content': 'Statue of Liberty Tour (New York): Visit America\'s iconic symbol. Ferry included. Budget: $20-25. Duration: 4 hours. Pre-book tickets online.',
                'metadata': {'type': 'activity', 'city': 'New York', 'category': 'landmark', 'price': 'budget'}
            },
            {
                'id': 'activity_muay_thai',
                'content': 'Muay Thai Boxing Class (Bangkok): Experience Thailand\'s national sport. Classes available for all levels. Cost: $30-50/session. Found throughout Bangkok.',
                'metadata': {'type': 'activity', 'city': 'Bangkok', 'category': 'experience', 'price': 'budget'}
            },
        ]
        
        # Add to knowledge base
        await self.add_documents('destinations', destinations)
        await self.add_documents('tips', tips)
        await self.add_documents('hotels', hotels)
        await self.add_documents('activities', activities)
        
        print("✓ Knowledge base seeded with travel data")


# Global knowledge base instance
kb = KnowledgeBase()


async def init_kb():
    """Initialize knowledge base on startup"""
    await kb.seed_knowledge_base()
