"""
Base Agent class for TravelAI Booking System
All specialized agents inherit from this class
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from abc import ABC, abstractmethod
from anthropic import Anthropic
from src.config import settings
from src.database import db


class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, agent_name: str, agent_description: str):
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.tools: List[Dict] = []
        self.conversation_history: List[Dict] = []
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    @abstractmethod
    def get_tools(self) -> List[Dict]:
        """Return available tools for this agent"""
        pass
    
    @abstractmethod
    async def execute_tool(self, tool_name: str, tool_input: Dict) -> Dict:
        """Execute a tool and return result"""
        pass
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        
        # Keep only recent history
        if len(self.conversation_history) > settings.conversation_history_limit:
            self.conversation_history.pop(0)
    
    def get_recent_context(self) -> List[Dict]:
        """Get recent conversation history for context"""
        return self.conversation_history[-settings.conversation_history_limit:]
    
    async def process_user_message(
        self,
        user_id: int,
        user_message: str,
        knowledge_context: Optional[str] = None
    ) -> str:
        """
        Process user message and return agent response
        Handles tool calling loop
        """
        # Add user message to history
        self.add_message("user", user_message)
        
        # Prepare messages for Claude
        messages = self.get_recent_context()
        
        # Add knowledge context if available
        if knowledge_context:
            user_message_with_context = f"{user_message}\n\n[KNOWLEDGE CONTEXT]\n{knowledge_context}"
            messages[-1]["content"] = user_message_with_context
        
        system_prompt = self.get_system_prompt()
        self.tools = self.get_tools()
        
        # Tool calling loop
        max_iterations = settings.max_tool_calls_per_request
        iteration = 0
        final_response = ""
        
        while iteration < max_iterations:
            iteration += 1
            
            # Call Claude with tool definitions
            response = self.client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=4096,
                system=system_prompt,
                tools=self.tools if self.tools else None,
                messages=messages
            )
            
            # Check if Claude wants to use a tool
            if response.stop_reason == "tool_use":
                # Process tool calls
                tool_results = []
                
                for content_block in response.content:
                    if content_block.type == "tool_use":
                        tool_name = content_block.name
                        tool_input = content_block.input
                        tool_use_id = content_block.id
                        
                        # Execute the tool
                        try:
                            tool_result = await self.execute_tool(tool_name, tool_input)
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": json.dumps(tool_result)
                            })
                        except Exception as e:
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": tool_use_id,
                                "content": f"Error: {str(e)}",
                                "is_error": True
                            })
                
                # Add assistant response and tool results to messages
                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
                
            elif response.stop_reason == "end_turn":
                # Claude finished with final response
                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        final_response = content_block.text
                break
            else:
                # Unexpected stop reason
                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        final_response = content_block.text
                break
        
        # Add final response to history
        if final_response:
            self.add_message("assistant", final_response)
        
        # Save conversation to database
        try:
            await db.save_conversation(
                user_id=user_id,
                agent_name=self.agent_name,
                role="user",
                message=user_message
            )
            await db.save_conversation(
                user_id=user_id,
                agent_name=self.agent_name,
                role="assistant",
                message=final_response
            )
        except Exception as e:
            print(f"Failed to save conversation: {e}")
        
        return final_response
    
    async def load_conversation_history(self, user_id: int):
        """Load conversation history from database"""
        try:
            history = await db.get_conversation_history(
                user_id=user_id,
                agent_name=self.agent_name,
                limit=20
            )
            
            # Convert to message format (reverse because DB returns newest first)
            for record in reversed(history):
                self.conversation_history.append({
                    "role": record['role'],
                    "content": record['message']
                })
        except Exception as e:
            print(f"Failed to load conversation history: {e}")