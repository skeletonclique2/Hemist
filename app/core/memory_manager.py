"""
Memory Manager for AI Agents System
Handles vector storage and retrieval of agent memories
"""

import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import structlog
import numpy as np
from openai import OpenAI
import os

logger = structlog.get_logger()

class MemoryManager:
    """Manages vector storage and retrieval of agent memories"""
    
    def __init__(self, openai_api_key: str = None):
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
        else:
            self.openai_client = None
            logger.warning("No OpenAI API key provided, using fallback embedding mode")
        
        self.memories: Dict[str, Dict[str, Any]] = {}
        self.embeddings: Dict[str, List[float]] = {}
        
        logger.info("Memory Manager initialized")
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate a hash for content to avoid duplicates"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def store_memory(self, content: str, memory_type: str = "general", 
                          importance_score: float = 0.5, metadata: Dict[str, Any] = None,
                          agent_id: str = None) -> str:
        """Store a new memory with vector embedding"""
        try:
            # Generate content hash
            content_hash = self._generate_content_hash(content)
            
            # Check if memory already exists
            if content_hash in self.memories:
                logger.debug(f"Memory already exists with hash: {content_hash}")
                return content_hash
            
            # Generate embedding using OpenAI
            embedding = await self._generate_embedding(content)
            
            # Create memory entry
            memory = {
                "id": content_hash,
                "content": content,
                "memory_type": memory_type,
                "importance_score": importance_score,
                "metadata": metadata or {},
                "agent_id": agent_id,
                "created_at": datetime.utcnow().isoformat(),
                "embedding": embedding
            }
            
            # Store in memory
            self.memories[content_hash] = memory
            self.embeddings[content_hash] = embedding
            
            logger.info(f"Stored memory: {content_hash} (type: {memory_type})")
            return content_hash
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return ""
    
    async def retrieve_memories(self, query: str = "", memory_type: str = "general", 
                               limit: int = 10, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve memories based on query and filters"""
        try:
            # Convert memories to list format
            memories_list = []
            for memory_id, memory in self.memories.items():
                # Apply type filter
                if memory_type != "general" and memory["memory_type"] != memory_type:
                    continue
                
                # Apply query filter (simple text search)
                if query and query.lower() not in memory["content"].lower():
                    continue
                
                # Apply additional filters
                if filters:
                    if not self._apply_filters(memory, filters):
                        continue
                
                memories_list.append(memory)
            
            # Sort by importance score (descending)
            memories_list.sort(key=lambda x: x["importance_score"], reverse=True)
            
            # Apply limit
            memories_list = memories_list[:limit]
            
            logger.debug(f"Retrieved {len(memories_list)} memories")
            return memories_list
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return []
    
    def _apply_filters(self, memory: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Apply filters to a memory entry"""
        try:
            for key, value in filters.items():
                if key == "min_importance":
                    if memory["importance_score"] < value:
                        return False
                elif key == "max_importance":
                    if memory["importance_score"] > value:
                        return False
                elif key == "date_from":
                    memory_date = datetime.fromisoformat(memory["created_at"])
                    filter_date = datetime.fromisoformat(value)
                    if memory_date < filter_date:
                        return False
                elif key == "date_to":
                    memory_date = datetime.fromisoformat(memory["created_at"])
                    filter_date = datetime.fromisoformat(value)
                    if memory_date > filter_date:
                        return False
                elif key == "metadata_filters":
                    for meta_key, meta_value in value.items():
                        if meta_key not in memory["metadata"] or memory["metadata"][meta_key] != meta_value:
                            return False
                elif key in memory and memory[key] != value:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply filters: {e}")
            return False
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            # Check if we have a valid client
            if not self.openai_client:
                logger.warning("No OpenAI API key available, using fallback embedding")
                # Return a simple hash-based vector as fallback
                import hashlib
                hash_obj = hashlib.md5(text.encode())
                hash_bytes = hash_obj.digest()
                # Convert to 1536-dimensional vector (simple but deterministic)
                vector = []
                for i in range(1536):
                    vector.append(float(hash_bytes[i % 16]) / 255.0)
                return vector
            
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 1536
    
    async def retrieve_similar_memories(self, query: str, memory_type: str = None, 
                                      limit: int = 10, similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Retrieve memories similar to the query"""
        try:
            if not self.memories:
                return []
            
            # Generate embedding for query
            query_embedding = await self._generate_embedding(query)
            
            # Calculate similarities
            similarities = []
            for memory_id, memory in self.memories.items():
                # Filter by type if specified
                if memory_type and memory["memory_type"] != memory_type:
                    continue
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(query_embedding, memory["embedding"])
                
                if similarity >= similarity_threshold:
                    similarities.append({
                        "memory_id": memory_id,
                        "similarity": similarity,
                        "memory": memory
                    })
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            
            result = []
            for item in similarities[:limit]:
                result.append({
                    **item["memory"],
                    "similarity_score": item["similarity"]
                })
            
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
        try:
            if not self.memories:
                return []
            
            results = []
            query_lower = query.lower()
            
            for memory_id, memory in self.memories.items():
                # Filter by type if specified
                if memory_type and memory["memory_type"] != memory_type:
                    continue
                
                # Check if query appears in content
                if query_lower in memory["content"].lower():
                    results.append({
                        **memory,
                        "relevance_score": 1.0  # Simple binary relevance for text search
                    })
            
            # Sort by importance and recency
            results.sort(key=lambda x: (x["importance_score"], x["created_at"]), reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    async def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific memory by ID"""
        return self.memories.get(memory_id)
    
    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing memory"""
        try:
            if memory_id not in self.memories:
                logger.warning(f"Memory not found: {memory_id}")
                return False
            
            # Update fields
            for key, value in updates.items():
                if key in self.memories[memory_id] and key != "id":
                    self.memories[memory_id][key] = value
            
            # Update timestamp
            self.memories[memory_id]["updated_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Updated memory: {memory_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update memory {memory_id}: {e}")
            return False
    
    async def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory"""
        try:
            if memory_id in self.memories:
                del self.memories[memory_id]
                if memory_id in self.embeddings:
                    del self.embeddings[memory_id]
                
                logger.info(f"Deleted memory: {memory_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            return False
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about stored memories"""
        try:
            if not self.memories:
                return {
                    "total_memories": 0,
                    "memory_types": {},
                    "total_embeddings": 0
                }
            
            # Count by type
            type_counts = {}
            for memory in self.memories.values():
                memory_type = memory["memory_type"]
                type_counts[memory_type] = type_counts.get(memory_type, 0) + 1
            
            return {
                "total_memories": len(self.memories),
                "memory_types": type_counts,
                "total_embeddings": len(self.embeddings),
                "embedding_dimension": len(next(iter(self.embeddings.values()))) if self.embeddings else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {}
    
    async def clear_memories(self, memory_type: str = None) -> int:
        """Clear all memories or memories of a specific type"""
        try:
            if memory_type:
                # Clear specific type
                to_delete = [mid for mid, mem in self.memories.items() 
                           if mem["memory_type"] == memory_type]
            else:
                # Clear all
                to_delete = list(self.memories.keys())
            
            for memory_id in to_delete:
                await self.delete_memory(memory_id)
            
            logger.info(f"Cleared {len(to_delete)} memories")
            return len(to_delete)
            
        except Exception as e:
            logger.error(f"Failed to clear memories: {e}")
            return 0
    
    async def export_memories(self, file_path: str = None) -> str:
        """Export memories to JSON file"""
        try:
            export_data = {
                "exported_at": datetime.utcnow().isoformat(),
                "total_memories": len(self.memories),
                "memories": list(self.memories.values())
            }
            
            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                logger.info(f"Exported memories to: {file_path}")
                return file_path
            else:
                return json.dumps(export_data, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to export memories: {e}")
            return "" 