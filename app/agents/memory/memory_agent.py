"""
Memory Agent for AI Agents System
Handles advanced context management, memory operations, and knowledge retrieval
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import structlog
import uuid
from collections import defaultdict

from app.core import BaseAgent, AgentType, AgentMemory
from app.core.memory_manager import MemoryManager

logger = structlog.get_logger()

class MemoryAgent(BaseAgent):
    """Memory Agent for advanced context management and memory operations"""
    
    def __init__(self, agent_id: str, name: str = "Memory Agent"):
        super().__init__(agent_id, AgentType.MEMORY, name)
        
        # Initialize memory manager
        self.memory_manager = MemoryManager()
        
        # Memory organization
        self.memory_categories = {
            "research": "Research findings and insights",
            "writing": "Content drafts and writing history",
            "editing": "Quality improvements and corrections",
            "workflow": "Workflow execution history",
            "knowledge": "General knowledge and facts",
            "context": "Contextual information and metadata"
        }
        
        # Memory indexing
        self.memory_index = defaultdict(list)
        self.temporal_index = defaultdict(list)
        self.semantic_index = defaultdict(list)
        
        logger.info(f"Memory Agent {name} initialized")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute memory management task"""
        try:
            operation = context.get("operation", "retrieve")
            memory_type = context.get("memory_type", "general")
            query = context.get("query", "")
            limit = context.get("limit", 10)
            
            await self.start_task(f"Memory operation: {operation} for {memory_type}")
            
            if operation == "store":
                result = await self._store_memory_operation(context)
            elif operation == "retrieve":
                result = await self._retrieve_memory_operation(context)
            elif operation == "organize":
                result = await self._organize_memory_operation(context)
            elif operation == "cleanup":
                result = await self._cleanup_memory_operation(context)
            elif operation == "analyze":
                result = await self._analyze_memory_operation(context)
            else:
                result = {"error": f"Unknown operation: {operation}"}
            
            await self.update_progress(1.0, f"Memory operation {operation} completed")
            await self.complete_task({
                "operation": operation,
                "memory_type": memory_type,
                "result_summary": str(result)[:100]
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Memory operation failed: {e}")
            await self.handle_error(e, "memory operation")
            return {"status": "error", "error": str(e)}
    
    async def _store_memory_operation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle memory storage operations"""
        try:
            content = context.get("content", "")
            memory_type = context.get("memory_type", "general")
            importance = context.get("importance", 0.5)
            metadata = context.get("metadata", {})
            
            # Store memory using memory manager
            memory_id = await self.memory_manager.store_memory(
                content, memory_type, importance, metadata
            )
            
            # Update local indexes
            await self._update_memory_indexes(memory_id, content, memory_type, metadata)
            
            # Store in agent memory for quick access
            await self.store_memory(
                f"Memory stored: {memory_type} - {content[:50]}...",
                "memory_operation",
                0.8,
                {"operation": "store", "memory_id": memory_id, "type": memory_type}
            )
            
            return {
                "status": "success",
                "operation": "store",
                "memory_id": memory_id,
                "memory_type": memory_type,
                "stored_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Memory storage operation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _retrieve_memory_operation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle memory retrieval operations"""
        try:
            query = context.get("query", "")
            memory_type = context.get("memory_type", "general")
            limit = context.get("limit", 10)
            filters = context.get("filters", {})
            
            # Retrieve memories using memory manager
            memories = await self.memory_manager.retrieve_memories(
                query, memory_type, limit, filters
            )
            
            # Apply additional filtering and ranking
            filtered_memories = await self._apply_advanced_filters(memories, filters)
            
            # Store retrieval operation
            await self.store_memory(
                f"Memory retrieved: {len(filtered_memories)} memories for {memory_type}",
                "memory_operation",
                0.7,
                {"operation": "retrieve", "count": len(filtered_memories), "type": memory_type}
            )
            
            return {
                "status": "success",
                "operation": "retrieve",
                "memories": filtered_memories,
                "count": len(filtered_memories),
                "memory_type": memory_type,
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Memory retrieval operation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _organize_memory_operation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle memory organization operations"""
        try:
            organization_type = context.get("organization_type", "categorize")
            
            if organization_type == "categorize":
                result = await self._categorize_memories()
            elif organization_type == "index":
                result = await self._rebuild_memory_indexes()
            elif organization_type == "cleanup":
                result = await self._cleanup_old_memories()
            else:
                result = {"error": f"Unknown organization type: {organization_type}"}
            
            # Store organization operation
            await self.store_memory(
                f"Memory organized: {organization_type} operation completed",
                "memory_operation",
                0.8,
                {"operation": "organize", "type": organization_type}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Memory organization operation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _cleanup_memory_operation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle memory cleanup operations"""
        try:
            cleanup_type = context.get("cleanup_type", "expired")
            threshold = context.get("threshold", 30)  # days
            
            if cleanup_type == "expired":
                result = await self._cleanup_expired_memories(threshold)
            elif cleanup_type == "low_importance":
                result = await self._cleanup_low_importance_memories()
            elif cleanup_type == "duplicates":
                result = await self._cleanup_duplicate_memories()
            else:
                result = {"error": f"Unknown cleanup type: {cleanup_type}"}
            
            return result
            
        except Exception as e:
            logger.error(f"Memory cleanup operation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _analyze_memory_operation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle memory analysis operations"""
        try:
            analysis_type = context.get("analysis_type", "overview")
            
            if analysis_type == "overview":
                result = await self._generate_memory_overview()
            elif analysis_type == "trends":
                result = await self._analyze_memory_trends()
            elif analysis_type == "quality":
                result = await self._analyze_memory_quality()
            else:
                result = {"error": f"Unknown analysis type: {analysis_type}"}
            
            return result
            
        except Exception as e:
            logger.error(f"Memory analysis operation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _update_memory_indexes(self, memory_id: str, content: str, 
                                   memory_type: str, metadata: Dict[str, Any]):
        """Update local memory indexes"""
        try:
            # Update memory index
            self.memory_index[memory_type].append(memory_id)
            
            # Update temporal index
            timestamp = datetime.now()
            self.temporal_index[timestamp.date()].append(memory_id)
            
            # Update semantic index (simple keyword-based)
            keywords = self._extract_keywords(content)
            for keyword in keywords:
                self.semantic_index[keyword.lower()].append(memory_id)
            
            logger.debug(f"Updated memory indexes for {memory_id}")
            
        except Exception as e:
            logger.error(f"Failed to update memory indexes: {e}")
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content"""
        try:
            # Simple keyword extraction (can be enhanced with NLP)
            words = content.lower().split()
            # Filter out common words and short words
            stop_words = {'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            keywords = [word for word in words if len(word) > 3 and word not in stop_words]
            # Return top 10 keywords
            return keywords[:10]
            
        except Exception as e:
            logger.error(f"Keyword extraction failed: {e}")
            return []
    
    async def _apply_advanced_filters(self, memories: List[AgentMemory], 
                                    filters: Dict[str, Any]) -> List[AgentMemory]:
        """Apply advanced filtering to memories"""
        try:
            filtered_memories = memories
            
            # Filter by importance threshold
            if "min_importance" in filters:
                min_importance = filters["min_importance"]
                filtered_memories = [m for m in filtered_memories if m.importance_score >= min_importance]
            
            # Filter by date range
            if "date_from" in filters and "date_to" in filters:
                date_from = datetime.fromisoformat(filters["date_from"])
                date_to = datetime.fromisoformat(filters["date_to"])
                filtered_memories = [
                    m for m in filtered_memories 
                    if date_from <= m.created_at <= date_to
                ]
            
            # Filter by metadata
            if "metadata_filters" in filters:
                metadata_filters = filters["metadata_filters"]
                for key, value in metadata_filters.items():
                    filtered_memories = [
                        m for m in filtered_memories 
                        if key in m.metadata and m.metadata[key] == value
                    ]
            
            return filtered_memories
            
        except Exception as e:
            logger.error(f"Advanced filtering failed: {e}")
            return memories
    
    async def _categorize_memories(self) -> Dict[str, Any]:
        """Categorize memories by type and content"""
        try:
            logger.info("Categorizing memories")
            
            # Get all memories
            all_memories = await self.memory_manager.retrieve_memories("", "general", 1000)
            
            # Categorize by type
            categories = defaultdict(list)
            for memory in all_memories:
                categories[memory.memory_type].append(memory)
            
            # Generate category summaries
            category_summaries = {}
            for category, memories in categories.items():
                category_summaries[category] = {
                    "count": len(memories),
                    "total_importance": sum(m.importance_score for m in memories),
                    "avg_importance": sum(m.importance_score for m in memories) / len(memories) if memories else 0,
                    "oldest": min(m.created_at for m in memories) if memories else None,
                    "newest": max(m.created_at for m in memories) if memories else None
                }
            
            return {
                "status": "success",
                "operation": "categorize",
                "categories": dict(category_summaries),
                "total_memories": len(all_memories)
            }
            
        except Exception as e:
            logger.error(f"Memory categorization failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _rebuild_memory_indexes(self) -> Dict[str, Any]:
        """Rebuild memory indexes"""
        try:
            logger.info("Rebuilding memory indexes")
            
            # Clear existing indexes
            self.memory_index.clear()
            self.temporal_index.clear()
            self.semantic_index.clear()
            
            # Get all memories and rebuild indexes
            all_memories = await self.memory_manager.retrieve_memories("", "general", 1000)
            
            for memory in all_memories:
                await self._update_memory_indexes(
                    memory.id, memory.content, memory.memory_type, memory.metadata
                )
            
            return {
                "status": "success",
                "operation": "rebuild_indexes",
                "indexes_rebuilt": ["memory", "temporal", "semantic"],
                "total_memories_indexed": len(all_memories)
            }
            
        except Exception as e:
            logger.error(f"Index rebuilding failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _cleanup_old_memories(self) -> Dict[str, Any]:
        """Clean up old memories"""
        try:
            logger.info("Cleaning up old memories")
            
            # Get memories older than 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            old_memories = []
            
            all_memories = await self.memory_manager.retrieve_memories("", "general", 1000)
            for memory in all_memories:
                if memory.created_at < cutoff_date and memory.importance_score < 0.7:
                    old_memories.append(memory)
            
            # Remove old memories (in a real system, you'd want to archive instead of delete)
            removed_count = len(old_memories)
            
            return {
                "status": "success",
                "operation": "cleanup_old",
                "memories_identified": removed_count,
                "cutoff_date": cutoff_date.isoformat(),
                "note": "In production, memories would be archived, not deleted"
            }
            
        except Exception as e:
            logger.error(f"Old memory cleanup failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _cleanup_expired_memories(self, threshold_days: int) -> Dict[str, Any]:
        """Clean up expired memories based on threshold"""
        try:
            logger.info(f"Cleaning up memories older than {threshold_days} days")
            
            cutoff_date = datetime.now() - timedelta(days=threshold_days)
            expired_memories = []
            
            all_memories = await self.memory_manager.retrieve_memories("", "general", 1000)
            for memory in all_memories:
                if memory.created_at < cutoff_date:
                    expired_memories.append(memory)
            
            return {
                "status": "success",
                "operation": "cleanup_expired",
                "expired_memories": len(expired_memories),
                "threshold_days": threshold_days,
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Expired memory cleanup failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _cleanup_low_importance_memories(self) -> Dict[str, Any]:
        """Clean up low importance memories"""
        try:
            logger.info("Cleaning up low importance memories")
            
            low_importance_memories = []
            all_memories = await self.memory_manager.retrieve_memories("", "general", 1000)
            
            for memory in all_memories:
                if memory.importance_score < 0.3:
                    low_importance_memories.append(memory)
            
            return {
                "status": "success",
                "operation": "cleanup_low_importance",
                "low_importance_memories": len(low_importance_memories),
                "importance_threshold": 0.3
            }
            
        except Exception as e:
            logger.error(f"Low importance memory cleanup failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _cleanup_duplicate_memories(self) -> Dict[str, Any]:
        """Clean up duplicate memories"""
        try:
            logger.info("Cleaning up duplicate memories")
            
            all_memories = await self.memory_manager.retrieve_memories("", "general", 1000)
            
            # Simple duplicate detection (content-based)
            content_map = {}
            duplicates = []
            
            for memory in all_memories:
                content_hash = hash(memory.content)
                if content_hash in content_map:
                    duplicates.append(memory)
                else:
                    content_map[content_hash] = memory
            
            return {
                "status": "success",
                "operation": "cleanup_duplicates",
                "duplicate_memories": len(duplicates),
                "unique_memories": len(content_map)
            }
            
        except Exception as e:
            logger.error(f"Duplicate memory cleanup failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _generate_memory_overview(self) -> Dict[str, Any]:
        """Generate comprehensive memory overview"""
        try:
            logger.info("Generating memory overview")
            
            all_memories = await self.memory_manager.retrieve_memories("", "general", 1000)
            
            # Calculate statistics
            total_memories = len(all_memories)
            total_importance = sum(m.importance_score for m in all_memories)
            avg_importance = total_importance / total_memories if total_memories > 0 else 0
            
            # Memory type distribution
            type_distribution = defaultdict(int)
            for memory in all_memories:
                type_distribution[memory.memory_type] += 1
            
            # Temporal distribution (last 7 days)
            recent_memories = [
                m for m in all_memories 
                if m.created_at > datetime.now() - timedelta(days=7)
            ]
            
            overview = {
                "status": "success",
                "operation": "overview",
                "total_memories": total_memories,
                "average_importance": avg_importance,
                "type_distribution": dict(type_distribution),
                "recent_memories": len(recent_memories),
                "memory_health": self._assess_memory_health(all_memories),
                "generated_at": datetime.now().isoformat()
            }
            
            return overview
            
        except Exception as e:
            logger.error(f"Memory overview generation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _analyze_memory_trends(self) -> Dict[str, Any]:
        """Analyze memory trends over time"""
        try:
            logger.info("Analyzing memory trends")
            
            all_memories = await self.memory_manager.retrieve_memories("", "general", 1000)
            
            # Group memories by date
            daily_memories = defaultdict(list)
            for memory in all_memories:
                date_key = memory.created_at.date()
                daily_memories[date_key].append(memory)
            
            # Calculate daily trends
            trends = []
            for date, memories in sorted(daily_memories.items()):
                trends.append({
                    "date": date.isoformat(),
                    "count": len(memories),
                    "avg_importance": sum(m.importance_score for m in memories) / len(memories),
                    "types": list(set(m.memory_type for m in memories))
                })
            
            return {
                "status": "success",
                "operation": "trends",
                "trends": trends,
                "total_days": len(trends),
                "date_range": {
                    "start": min(trends, key=lambda x: x["date"])["date"] if trends else None,
                    "end": max(trends, key=lambda x: x["date"])["date"] if trends else None
                }
            }
            
        except Exception as e:
            logger.error(f"Memory trend analysis failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _analyze_memory_quality(self) -> Dict[str, Any]:
        """Analyze memory quality metrics"""
        try:
            logger.info("Analyzing memory quality")
            
            all_memories = await self.memory_manager.retrieve_memories("", "general", 1000)
            
            # Quality metrics
            high_quality = [m for m in all_memories if m.importance_score >= 0.8]
            medium_quality = [m for m in all_memories if 0.5 <= m.importance_score < 0.8]
            low_quality = [m for m in all_memories if m.importance_score < 0.5]
            
            # Content length analysis
            content_lengths = [len(m.content) for m in all_memories]
            avg_content_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
            
            quality_analysis = {
                "status": "success",
                "operation": "quality_analysis",
                "quality_distribution": {
                    "high": len(high_quality),
                    "medium": len(medium_quality),
                    "low": len(low_quality)
                },
                "content_metrics": {
                    "average_length": avg_content_length,
                    "total_content": sum(content_lengths),
                    "shortest": min(content_lengths) if content_lengths else 0,
                    "longest": max(content_lengths) if content_lengths else 0
                },
                "recommendations": self._generate_quality_recommendations(all_memories)
            }
            
            return quality_analysis
            
        except Exception as e:
            logger.error(f"Memory quality analysis failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _assess_memory_health(self, memories: List[AgentMemory]) -> str:
        """Assess overall memory health"""
        try:
            if not memories:
                return "empty"
            
            # Calculate health score
            total_importance = sum(m.importance_score for m in memories)
            avg_importance = total_importance / len(memories)
            
            # Recent activity
            recent_count = len([m for m in memories if m.created_at > datetime.now() - timedelta(days=1)])
            
            if avg_importance >= 0.7 and recent_count >= 5:
                return "excellent"
            elif avg_importance >= 0.5 and recent_count >= 2:
                return "good"
            elif avg_importance >= 0.3:
                return "fair"
            else:
                return "poor"
                
        except Exception as e:
            logger.error(f"Memory health assessment failed: {e}")
            return "unknown"
    
    def _generate_quality_recommendations(self, memories: List[AgentMemory]) -> List[str]:
        """Generate recommendations for improving memory quality"""
        try:
            recommendations = []
            
            if not memories:
                recommendations.append("No memories available for analysis")
                return recommendations
            
            # Analyze importance distribution
            low_importance_count = len([m for m in memories if m.importance_score < 0.5])
            if low_importance_count > len(memories) * 0.3:
                recommendations.append("Consider filtering out low-importance memories")
            
            # Analyze content diversity
            memory_types = set(m.memory_type for m in memories)
            if len(memory_types) < 3:
                recommendations.append("Diversify memory types for better context")
            
            # Analyze recency
            old_memories = [m for m in memories if m.created_at < datetime.now() - timedelta(days=30)]
            if len(old_memories) > len(memories) * 0.5:
                recommendations.append("Consider archiving old memories")
            
            if not recommendations:
                recommendations.append("Memory quality is good, no immediate actions needed")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Quality recommendation generation failed: {e}")
            return ["Unable to generate recommendations due to error"]
    
    async def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        try:
            all_memories = await self.memory_manager.retrieve_memories("", "general", 1000)
            
            stats = {
                "total_memories": len(all_memories),
                "memory_types": list(set(m.memory_type for m in all_memories)),
                "importance_range": {
                    "min": min(m.importance_score for m in all_memories) if all_memories else 0,
                    "max": max(m.importance_score for m in all_memories) if all_memories else 0,
                    "average": sum(m.importance_score for m in all_memories) / len(all_memories) if all_memories else 0
                },
                "temporal_range": {
                    "oldest": min(m.created_at for m in all_memories) if all_memories else None,
                    "newest": max(m.created_at for m in all_memories) if all_memories else None
                },
                "index_status": {
                    "memory_index": len(self.memory_index),
                    "temporal_index": len(self.temporal_index),
                    "semantic_index": len(self.semantic_index)
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get memory statistics: {e}")
            return {"error": str(e)} 