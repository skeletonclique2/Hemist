#!/usr/bin/env python3
"""
Test script to verify agent memory integration
"""

import asyncio
import uuid
from typing import Dict, Any
from app.core.base_agent import BaseAgent, AgentType
from app.database.connection import init_db
from app.database.models import Agent

class TestAgent(BaseAgent):
    """A simple test agent for memory integration testing"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, AgentType.RESEARCHER, "Test Research Agent")
    
    async def _execute_impl(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simple test implementation"""
        await self.store_memory(
            content=f"Test execution with context: {context}",
            memory_type="test_execution",
            importance_score=0.8,
            metadata={"test": True, "context": context}
        )
        return {"status": "success", "message": "Test execution completed"}

async def test_agent_memory_integration():
    """Test the complete agent memory integration"""
    print("=== Testing Agent Memory Integration ===")
    
    # Initialize database
    await init_db()
    
    # Create test agent
    agent_id = str(uuid.uuid4())
    agent = TestAgent(agent_id)
    
    # Test 1: Store memories
    print("\n--- Test 1: Storing Memories ---")
    memory1 = await agent.store_memory(
        content="This is a test memory about AI research",
        memory_type="research",
        importance_score=0.9,
        metadata={"topic": "AI", "source": "test"}
    )
    print(f"Stored memory 1: {memory1}")
    
    memory2 = await agent.store_memory(
        content="Another test memory about machine learning",
        memory_type="research",
        importance_score=0.8,
        metadata={"topic": "ML", "source": "test"}
    )
    print(f"Stored memory 2: {memory2}")
    
    # Test 2: Retrieve memories
    print("\n--- Test 2: Retrieving Memories ---")
    memories = await agent.retrieve_memories(memory_type="research")
    print(f"Retrieved {len(memories)} research memories:")
    for mem in memories:
        print(f"  - {mem.content} (importance: {mem.importance_score})")
    
    # Test 3: Similarity search
    print("\n--- Test 3: Similarity Search ---")
    similar = await agent.retrieve_similar_memories("artificial intelligence", limit=3)
    print(f"Found {len(similar)} similar memories:")
    for mem in similar:
        print(f"  - {mem.content}")
    
    # Test 4: Agent execution with memory
    print("\n--- Test 4: Agent Execution with Memory ---")
    result = await agent.execute({"task": "test memory integration"})
    print(f"Execution result: {result}")
    
    # Test 5: Retrieve execution memories
    print("\n--- Test 5: Retrieving Execution Memories ---")
    exec_memories = await agent.retrieve_memories(memory_type="test_execution")
    print(f"Retrieved {len(exec_memories)} execution memories:")
    for mem in exec_memories:
        print(f"  - {mem.content}")
    
    print("\n=== All Tests Completed Successfully ===")

if __name__ == "__main__":
    asyncio.run(test_agent_memory_integration())
