"""
Inter-Agent Communication System
Handles message passing and coordination between agents
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Callable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import structlog
from enum import Enum

logger = structlog.get_logger()

class MessageType(str, Enum):
    """Types of messages between agents"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    ERROR_NOTIFICATION = "error_notification"
    MEMORY_SHARE = "memory_share"
    WORKFLOW_EVENT = "workflow_event"
    COORDINATION = "coordination"

class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class AgentMessage:
    """Message structure for inter-agent communication"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    recipient_id: str = ""
    message_type: MessageType = MessageType.COORDINATION
    priority: MessagePriority = MessagePriority.NORMAL
    content: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    delivered: bool = False
    acknowledged: bool = False

class AgentCommunicationHub:
    """Central hub for agent communication"""
    
    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.message_queues: Dict[str, asyncio.Queue] = {}
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.broadcast_handlers: List[Callable] = []
        self.running = False
        
        logger.info("Agent Communication Hub initialized")
    
    async def register_agent(self, agent_id: str, agent_name: str, 
                           message_handler: Callable = None) -> bool:
        """Register an agent with the communication hub"""
        try:
            if agent_id in self.agents:
                logger.warning(f"Agent {agent_id} already registered")
                return False
            
            # Create message queue for agent
            self.message_queues[agent_id] = asyncio.Queue()
            self.message_handlers[agent_id] = []
            
            # Register agent
            self.agents[agent_id] = {
                "id": agent_id,
                "name": agent_name,
                "registered_at": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            # Add message handler if provided
            if message_handler:
                self.message_handlers[agent_id].append(message_handler)
            
            logger.info(f"Agent {agent_name} ({agent_id}) registered")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent_id}: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the communication hub"""
        try:
            if agent_id not in self.agents:
                logger.warning(f"Agent {agent_id} not registered")
                return False
            
            # Remove agent
            del self.agents[agent_id]
            
            # Clean up message queue
            if agent_id in self.message_queues:
                del self.message_queues[agent_id]
            
            # Clean up message handlers
            if agent_id in self.message_handlers:
                del self.message_handlers[agent_id]
            
            logger.info(f"Agent {agent_id} unregistered")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False
    
    async def send_message(self, message: AgentMessage) -> bool:
        """Send a message to a specific agent"""
        try:
            if message.recipient_id not in self.agents:
                logger.warning(f"Recipient agent {message.recipient_id} not found")
                return False
            
            # Check if message has expired
            if message.expires_at and datetime.utcnow() > message.expires_at:
                logger.warning(f"Message {message.id} has expired")
                return False
            
            # Add to recipient's queue
            await self.message_queues[message.recipient_id].put(message)
            
            logger.debug(f"Message {message.id} sent to {message.recipient_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message {message.id}: {e}")
            return False
    
    async def broadcast_message(self, message: AgentMessage, 
                              exclude_sender: bool = True) -> int:
        """Broadcast a message to all registered agents"""
        try:
            sent_count = 0
            
            for agent_id in self.agents:
                if exclude_sender and agent_id == message.sender_id:
                    continue
                
                # Create a copy of the message for each recipient
                broadcast_msg = AgentMessage(
                    sender_id=message.sender_id,
                    recipient_id=agent_id,
                    message_type=message.message_type,
                    priority=message.priority,
                    content=message.content,
                    metadata=message.metadata,
                    expires_at=message.expires_at
                )
                
                if await self.send_message(broadcast_msg):
                    sent_count += 1
            
            logger.info(f"Broadcast message sent to {sent_count} agents")
            return sent_count
            
        except Exception as e:
            logger.error(f"Failed to broadcast message: {e}")
            return 0
    
    async def get_messages(self, agent_id: str, timeout: float = 1.0) -> List[AgentMessage]:
        """Get all pending messages for an agent"""
        try:
            if agent_id not in self.message_queues:
                return []
            
            messages = []
            queue = self.message_queues[agent_id]
            
            # Get all available messages
            while not queue.empty():
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=timeout)
                    messages.append(message)
                except asyncio.TimeoutError:
                    break
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get messages for agent {agent_id}: {e}")
            return []
    
    async def acknowledge_message(self, message_id: str, agent_id: str) -> bool:
        """Acknowledge receipt of a message"""
        try:
            # Find the message in the agent's queue and mark as acknowledged
            # This is a simplified implementation
            logger.debug(f"Message {message_id} acknowledged by agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to acknowledge message {message_id}: {e}")
            return False
    
    async def add_message_handler(self, agent_id: str, handler: Callable) -> bool:
        """Add a message handler for an agent"""
        try:
            if agent_id not in self.message_handlers:
                logger.warning(f"Agent {agent_id} not registered")
                return False
            
            self.message_handlers[agent_id].append(handler)
            logger.info(f"Message handler added for agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add message handler for agent {agent_id}: {e}")
            return False
    
    async def add_broadcast_handler(self, handler: Callable) -> bool:
        """Add a broadcast message handler"""
        try:
            self.broadcast_handlers.append(handler)
            logger.info("Broadcast handler added")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add broadcast handler: {e}")
            return False
    
    async def start(self):
        """Start the communication hub"""
        try:
            self.running = True
            logger.info("Agent Communication Hub started")
            
            # Start message processing loop
            asyncio.create_task(self._message_processor())
            
        except Exception as e:
            logger.error(f"Failed to start communication hub: {e}")
    
    async def stop(self):
        """Stop the communication hub"""
        try:
            self.running = False
            logger.info("Agent Communication Hub stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop communication hub: {e}")
    
    async def _message_processor(self):
        """Background message processor"""
        while self.running:
            try:
                # Process messages for each agent
                for agent_id, handlers in self.message_handlers.items():
                    if not handlers:
                        continue
                    
                    messages = await self.get_messages(agent_id, timeout=0.1)
                    
                    for message in messages:
                        # Call all handlers for the agent
                        for handler in handlers:
                            try:
                                if asyncio.iscoroutinefunction(handler):
                                    await handler(message)
                                else:
                                    handler(message)
                            except Exception as e:
                                logger.error(f"Message handler failed for agent {agent_id}: {e}")
                        
                        # Mark message as delivered
                        message.delivered = True
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Message processor error: {e}")
                await asyncio.sleep(1.0)  # Wait before retrying
    
    def get_hub_status(self) -> Dict[str, Any]:
        """Get communication hub status"""
        return {
            "running": self.running,
            "registered_agents": len(self.agents),
            "total_message_queues": len(self.message_queues),
            "total_handlers": sum(len(handlers) for handlers in self.message_handlers.values()),
            "broadcast_handlers": len(self.broadcast_handlers)
        }
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent"""
        if agent_id not in self.agents:
            return None
        
        agent_info = self.agents[agent_id].copy()
        
        # Add queue information
        if agent_id in self.message_queues:
            agent_info["queue_size"] = self.message_queues[agent_id].qsize()
        
        # Add handler information
        if agent_id in self.message_handlers:
            agent_info["handler_count"] = len(self.message_handlers[agent_id])
        
        return agent_info 