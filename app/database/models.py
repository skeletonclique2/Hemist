from sqlalchemy import Column, String, DateTime, Float, Text, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.connection import Base
import uuid

class Agent(Base):
    """Agent model representing different AI agents in the system"""
    __tablename__ = "agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    agent_type = Column(String(100), nullable=False)
    status = Column(String(50), default='idle')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    states = relationship("AgentState", back_populates="agent", cascade="all, delete-orphan")
    memories = relationship("AgentMemory", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Agent(name='{self.name}', type='{self.agent_type}', status='{self.status}')>"

class AgentState(Base):
    """Agent state model for storing agent state data"""
    __tablename__ = "agent_states"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    state_data = Column(JSONB, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    agent = relationship("Agent", back_populates="states")
    
    def __repr__(self):
        return f"<AgentState(agent_id='{self.agent_id}', created_at='{self.created_at}')>"

class ContentEmbedding(Base):
    """Content embedding model for vector similarity search"""
    __tablename__ = "content_embeddings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_hash = Column(String(64), unique=True, nullable=False, index=True)
    content_text = Column(Text, nullable=False)
    embedding = Column("embedding", Text)  # Will be converted to vector type by pgvector
    content_metadata = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ContentEmbedding(content_hash='{self.content_hash}', created_at='{self.created_at}')>"

class AgentMemory(Base):
    """Agent memory model for storing agent memories"""
    __tablename__ = "agent_memory"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    memory_type = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    importance_score = Column(Float, default=0.5)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    agent = relationship("Agent", back_populates="memories")
    
    def __repr__(self):
        return f"<AgentMemory(agent_id='{self.agent_id}', type='{self.memory_type}', score='{self.importance_score}')>"

class Workflow(Base):
    """Workflow model for storing agent workflow data"""
    __tablename__ = "workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    workflow_data = Column(JSONB, nullable=False)
    status = Column(String(50), default='pending')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Workflow(name='{self.name}', status='{self.status}')>"

# Create indexes for performance
Index('idx_agents_type', Agent.agent_type)
Index('idx_agents_status', Agent.status)
Index('idx_content_embeddings_hash', ContentEmbedding.content_hash)
Index('idx_agent_memory_agent', AgentMemory.agent_id)
Index('idx_agent_memory_type', AgentMemory.memory_type) 