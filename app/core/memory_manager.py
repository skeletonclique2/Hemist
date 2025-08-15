"""
Memory Manager for AI Agents System
Handles vector storage and retrieval of agent memories
"""

import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
import numpy as np
from openai import OpenAI
import os

logger = structlog.get_logger()

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.database.models import AgentMemory, ContentEmbedding

class MemoryManager:
    """Manages vector storage and retrieval of agent memories with DB integration"""
    
    def __init__(self, db_session: AsyncSession, openai_api_key: str = None):
        self.db_session = db_session
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
        else:
            self.openai_client = None
            logger.warning("No OpenAI API key provided, using fallback embedding mode")
        
        logger.info("Memory Manager initialized with DB session")
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate a hash for content to avoid duplicates"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            if not self.openai_client:
                # Fallback: generate random embedding
                logger.warning("Using fallback embedding generation")
                return np.random.randn(1536).tolist()
            
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return np.random.randn(1536).tolist()
    
    async def store_memory(self, content: str, memory_type: str = "general", 
                          importance_score: float = 0.5, metadata: Dict[str, Any] = None,
                          agent_id: str = None) -> str:
        """Store a new memory with vector embedding in DB"""
        try:
            content_hash = self._generate_content_hash(content)
            
            # Check if memory already exists in DB
            query = await self.db_session.execute(
                select(ContentEmbedding).where(ContentEmbedding.content_hash == content_hash)
            )
            existing_embedding = query.scalar_one_or_none()
            if existing_embedding:
                logger.debug(f"Memory already exists in DB with hash: {content_hash}")
                return content_hash
            
            # Generate embedding
            embedding = await self._generate_embedding(content)
            
            # Create ContentEmbedding record
            content_embedding = ContentEmbedding(
                content_hash=content_hash,
                content_text=content,
                embedding=embedding,
                content_metadata=metadata or {}
            )
            self.db_session.add(content_embedding)
            
            # Create AgentMemory record
            agent_memory = AgentMemory(
                agent_id=agent_id,
                memory_type=memory_type,
                content=content,
                importance_score=importance_score
            )
            self.db_session.add(agent_memory)
            
            await self.db_session.commit()
            
            logger.info(f"Stored memory in DB: {content_hash} (type: {memory_type})")
            return content_hash
            
        except Exception as e:
            logger.error(f"Failed to store memory in DB: {e}")
            await self.db_session.rollback()
            return ""
    
    async def retrieve_memories(self, query: str = "", memory_type: str = "general", 
                               limit: int = 10, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve memories based on query and filters"""
        try:
            stmt = select(AgentMemory)
            if memory_type != "general":
                stmt = stmt.where(AgentMemory.memory_type == memory_type)
            if query:
                stmt = stmt.where(AgentMemory.content.ilike(f"%{query}%"))
            if filters:
                for key, value in filters.items():
                    stmt = stmt.where(getattr(AgentMemory, key) == value)
            stmt = stmt.limit(limit)
            
            result = await self.db_session.execute(stmt)
            memories = result.scalars().all()
            
            # Convert to dicts
            memories_list = []
            for mem in memories:
                mem_dict = {
                    "id": str(mem.id),
                    "agent_id": mem.agent_id,
                    "memory_type": mem.memory_type,
                    "content": mem.content,
                    "importance_score": mem.importance_score,
                    "created_at": mem.created_at.isoformat() if mem.created_at else None
                }
                memories_list.append(mem_dict)
            
            return memories_list
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return []
    
    async def retrieve_similar_memories(self, query: str, memory_type: str = None, 
                                      limit: int = 10, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Retrieve memories similar to the query using vector similarity"""
        try:
            # Generate embedding for query
            query_embedding = await self._generate_embedding(query)
            
            # Get all content embeddings from database
            stmt = select(ContentEmbedding)
            result = await self.db_session.execute(stmt)
            embeddings = result.scalars().all()
            
            if not embeddings:
                return []
            
            # Calculate similarities
            similarities = []
            for embedding_record in embeddings:
                try:
                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(query_embedding, embedding_record.embedding)
                    
                    if similarity >= similarity_threshold:
                        similarities.append({
                            "content_hash": embedding_record.content_hash,
                            "similarity": similarity,
                            "content": embedding_record.content_text,
                            "metadata": embedding_record.content_metadata,
                            "created_at": embedding_record.created_at.isoformat() if embedding_record.created_at else None
                        })
                except Exception as e:
                    logger.warning(f"Failed to process embedding: {e}")
                    continue
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            result = similarities[:limit]
            logger.info(f"Retrieved {len(result)} similar memories for query")
            return result
            
        except Exception as e:
            logger.error(f"Failed to retrieve similar memories: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            vec1_array = np.array(vec1)
            vec2_array = np.array(vec2)
            
            # Normalize vectors
            norm1 = np.linalg.norm(vec1_array)
            norm2 = np.linalg.norm(vec2_array)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            # Calculate cosine similarity
            similarity = np.dot(vec1_array, vec2_array) / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Failed to calculate cosine similarity: {e}")
            return 0.0
    
    async def search_memories(self, query: str, memory_type: str = None, 
                            limit: int = 10) -> List[Dict[str, Any]]:
        """Search memories by text content"""
        return await self.retrieve_memories(query=query, memory_type=memory_type or "general", limit=limit)
    
    async def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific memory by ID"""
        try:
            stmt = select(AgentMemory).where(AgentMemory.id == memory_id)
            result = await self.db_session.execute(stmt)
            memory = result.scalar_one_or_none()
            if memory:
                return {
                    "id": str(memory.id),
                    "agent_id": memory.agent_id,
                    "memory_type": memory.memory_type,
                    "content": memory.content,
                    "importance_score": memory.importance_score,
                    "created_at": memory.created_at.isoformat() if memory.created_at else None
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get memory {memory_id}: {e}")
            return None

    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory"""
        try:
            stmt = select(AgentMemory).where(AgentMemory.id == memory_id)
            result = await self.db_session.execute(stmt)
            memory = result.scalar_one_or_none()
            
            if memory:
                for key, value in updates.items():
                    if hasattr(memory, key):
                        setattr(memory, key, value)
                
                await self.db_session.commit()
                logger.info(f"Updated memory: {memory_id}")
                return True
            
            logger.warning(f"Memory not found for update: {memory_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            await self.db_session.rollback()
            return False

    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        try:
            stmt = select(AgentMemory).where(AgentMemory.id == memory_id)
            result = await self.db_session.execute(stmt)
            memory = result.scalar_one_or_none()

            if memory:
                await self.db_session.delete(memory)
                await self.db_session.commit()
                logger.info(f"Deleted memory: {memory_id}")
                return True
            
            logger.warning(f"Memory not found for deletion: {memory_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            await self.db_session.rollback()
            return False
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories"""
        try:
            # Total memories
            total_memories_query = await self.db_session.execute(select(func.count(AgentMemory.id)))
            total_memories = total_memories_query.scalar_one()
            
            # Total embeddings
            total_embeddings_query = await self.db_session.execute(select(func.count(ContentEmbedding.id)))
            total_embeddings = total_embeddings_query.scalar_one()
            
            # Memory types
            memory_types_query = await self.db_session.execute(
                select(AgentMemory.memory_type, func.count(AgentMemory.id))
                .group_by(AgentMemory.memory_type)
            )
            memory_types = {row[0]: row[1] for row in memory_types_query.all()}
            
            return {
                "total_memories": total_memories,
                "memory_types": memory_types,
                "total_embeddings": total_embeddings
            }
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {}
    
    async def clear_memories(self, memory_type: str = None) -> int:
        """Clear all memories or memories of a specific type"""
        try:
            if memory_type:
                stmt = select(AgentMemory).where(AgentMemory.memory_type == memory_type)
            else:
                stmt = select(AgentMemory)
            
            result = await self.db_session.execute(stmt)
            memories = result.scalars().all()
            
            count = 0
            for mem in memories:
                await self.db_session.delete(mem)
                count += 1
            
            await self.db_session.commit()
            logger.info(f"Cleared {count} memories")
            return count
            
        except Exception as e:
            logger.error(f"Failed to clear memories: {e}")
            await self.db_session.rollback()
            return 0
    
    async def export_memories(self, file_path: str = None) -> str:
        """Export all memories to a JSON file"""
        try:
            stmt = select(AgentMemory)
            result = await self.db_session.execute(stmt)
            memories = result.scalars().all()
            
            memories_data = []
            for mem in memories:
                memories_data.append({
                    "id": str(mem.id),
                    "agent_id": mem.agent_id,
                    "memory_type": mem.memory_type,
                    "content": mem.content,
                    "importance_score": mem.importance_score,
                    "created_at": mem.created_at.isoformat() if mem.created_at else None
                })
            
            export_data = {
                "exported_at": datetime.utcnow().isoformat(),
                "memories": memories_data
            }
            
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2)
                logger.info(f"Exported {len(memories_data)} memories to {file_path}")
                return file_path
            else:
                return json.dumps(export_data, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to export memories: {e}")
            return ""
