"""
Base Agent Class for AI Agents System
Provides common functionality for all agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import structlog
from enum import Enum

import langsmith
from prometheus_client import Counter

logger = structlog.get_logger()

# Prometheus metrics for agent actions
AGENT_EXECUTIONS = Counter("agent_executions_total", "Total agent executions", ["agent_type"])
AGENT_COMPLETIONS = Counter("agent_completions_total", "Total agent completions", ["agent_type"])
AGENT_ERRORS = Counter("agent_errors_total", "Total agent errors", ["agent_type"])

class AgentStatus(str, Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    COMPLETED = "completed"

class AgentType(str, Enum):
    """Agent type enumeration"""
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    WRITER = "writer"
    EDITOR = "editor"
    MEMORY = "memory"

@dataclass
class AgentMemory:
    """Memory entry for an agent"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    memory_type: str = "general"
    importance_score: float = 0.5
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentState:
    """Current state of an agent"""
    agent_id: str
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    task_progress: float = 0.0
    last_activity: datetime = field(default_factory=datetime.utcnow)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, agent_id: str, agent_type: AgentType, name: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.status = AgentStatus.IDLE
        self.memories: List[AgentMemory] = []
        self.state = AgentState(agent_id=agent_id)
        
        logger.info(f"Initialized {self.agent_type} agent: {name} ({agent_id})")
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main functionality
        Must be implemented by subclasses
        """
        # LangSmith tracing and Prometheus metrics
        AGENT_EXECUTIONS.labels(agent_type=self.agent_type.value).inc()
        with langsmith.trace(f"{self.agent_type.value}_execute", agent_id=self.agent_id, agent_name=self.name):
            return await self._execute_impl(context)

    @abstractmethod
    async def _execute_impl(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Subclasses must implement this method instead of execute.
        """
        pass
    
    async def initialize(self, config: Dict[str, Any] = None) -> bool:
        """Initialize the agent with configuration"""
        try:
            logger.info(f"Initializing agent {self.name}")
            self.status = AgentStatus.IDLE
            self.state.status = AgentStatus.IDLE
            
            if config:
                # Apply configuration
                for key, value in config.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
            
            logger.info(f"Agent {self.name} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize agent {self.name}: {e}")
            self.status = AgentStatus.ERROR
            self.state.status = AgentStatus.ERROR
            self.state.error_message = str(e)
            return False
    
    async def start_task(self, task_description: str) -> bool:
        """Start a new task"""
        try:
            logger.info(f"Agent {self.name} starting task: {task_description}")
            self.status = AgentStatus.BUSY
            self.state.status = AgentStatus.BUSY
            self.state.current_task = task_description
            self.state.task_progress = 0.0
            self.state.last_activity = datetime.utcnow()
            return True
            
        except Exception as e:
            logger.error(f"Failed to start task for agent {self.name}: {e}")
            return False
    
    async def update_progress(self, progress: float, message: str = None) -> bool:
        """Update task progress"""
        try:
            self.state.task_progress = max(0.0, min(1.0, progress))
            if message:
                logger.info(f"Agent {self.name} progress: {progress:.1%} - {message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update progress for agent {self.name}: {e}")
            return False
    
    async def complete_task(self, result: Dict[str, Any] = None) -> bool:
        """Complete the current task"""
        try:
            logger.info(f"Agent {self.name} completed task: {self.state.current_task}")
            AGENT_COMPLETIONS.labels(agent_type=self.agent_type.value).inc()
            self.status = AgentStatus.COMPLETED
            self.state.status = AgentStatus.COMPLETED
            self.state.task_progress = 1.0
            self.state.last_activity = datetime.utcnow()
            
            # Store result in memory if provided
            if result:
                await self.store_memory(
                    content=str(result),
                    memory_type="task_result",
                    importance_score=0.8
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete task for agent {self.name}: {e}")
            return False
    
    async def handle_error(self, error: Exception, context: str = None) -> bool:
        """Handle errors during execution"""
        try:
            error_msg = f"Error in {context or 'execution'}: {str(error)}"
            logger.error(f"Agent {self.name} encountered error: {error_msg}")
            AGENT_ERRORS.labels(agent_type=self.agent_type.value).inc()
            self.status = AgentStatus.ERROR
            self.state.status = AgentStatus.ERROR
            self.state.error_message = error_msg
            self.state.last_activity = datetime.utcnow()
            
            # Store error in memory for learning
            await self.store_memory(
                content=error_msg,
                memory_type="error",
                importance_score=0.9
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to handle error for agent {self.name}: {e}")
            return False
    
    async def store_memory(self, content: str, memory_type: str = "general", 
                          importance_score: float = 0.5, metadata: Dict[str, Any] = None) -> str:
        """Store a new memory"""
        try:
            memory = AgentMemory(
                content=content,
                memory_type=memory_type,
                importance_score=importance_score,
                metadata=metadata or {}
            )
            
            self.memories.append(memory)
            logger.debug(f"Agent {self.name} stored memory: {memory.id}")
            return memory.id
            
        except Exception as e:
            logger.error(f"Failed to store memory for agent {self.name}: {e}")
            return ""
    
    async def retrieve_memories(self, query: str = None, memory_type: str = None, 
                              limit: int = 10) -> List[AgentMemory]:
        """Retrieve memories based on criteria"""
        try:
            memories = self.memories
            
            # Filter by type if specified
            if memory_type:
                memories = [m for m in memories if m.memory_type == memory_type]
            
            # Filter by query if specified (simple text search for now)
            if query:
                query_lower = query.lower()
                memories = [m for m in memories if query_lower in m.content.lower()]
            
            # Sort by importance and recency
            memories.sort(key=lambda m: (m.importance_score, m.created_at), reverse=True)
            
            return memories[:limit]
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories for agent {self.name}: {e}")
            return []
    
    async def reset(self) -> bool:
        """Reset agent to idle state"""
        try:
            logger.info(f"Resetting agent {self.name}")
            self.status = AgentStatus.IDLE
            self.state = AgentState(agent_id=self.agent_id)
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset agent {self.name}: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type.value,
            "status": self.status.value,
            "current_task": self.state.current_task,
            "task_progress": self.state.task_progress,
            "last_activity": self.state.last_activity.isoformat(),
            "error_message": self.state.error_message,
            "memory_count": len(self.memories)
        }
    
    def get_health(self) -> Dict[str, Any]:
        """Get agent health information"""
        return {
            "agent_id": self.agent_id,
            "status": "healthy" if self.status != AgentStatus.ERROR else "unhealthy",
            "memory_usage": len(self.memories),
            "uptime": (datetime.utcnow() - self.state.last_activity).total_seconds(),
            "last_error": self.state.error_message
        }
