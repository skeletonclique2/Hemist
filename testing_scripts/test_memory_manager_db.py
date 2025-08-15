import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.memory_manager import MemoryManager
from app.database.connection import ASYNC_DATABASE_URL, init_db
from app.database.models import Agent # Import the Agent model

async def test_memory_manager():
    # Setup async engine and session
    engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
    
    # Initialize DB schema
    await init_db()
    
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        memory_manager = MemoryManager(session)
        
        # --- Setup: Create a dummy agent for FK constraint ---
        test_agent = Agent(name=f"Test Agent {uuid.uuid4()}", agent_type="test_runner")
        session.add(test_agent)
        await session.commit()
        await session.refresh(test_agent)
        agent_id = test_agent.id
        print(f"--- Created dummy agent with ID: {agent_id} ---")

        # 1. Clear any previous test data
        print("\n--- Clearing old test memories ---")
        cleared_count = await memory_manager.clear_memories(memory_type="test")
        print(f"Cleared {cleared_count} old test memories.")

        # 2. Test storing a memory
        print("\n--- Testing memory storage ---")
        content = f"This is a test memory content for vector DB integration. Test run: {uuid.uuid4()}"
        memory_type = "test"
        importance_score = 0.9
        metadata = {"source": "unit_test", "timestamp": "2025-08-15"}
        
        stored_hash = await memory_manager.store_memory(
            content, memory_type, importance_score, metadata, agent_id=str(agent_id)
        )
        print(f"Stored memory with content hash: {stored_hash}")
        assert stored_hash is not None and len(stored_hash) > 0

        # 3. Test retrieving memories
        print("\n--- Testing memory retrieval ---")
        memories = await memory_manager.retrieve_memories(query="vector DB", memory_type="test")
        print(f"Retrieved memories count: {len(memories)}")
        assert len(memories) > 0
        for mem in memories:
            print(mem)
            assert str(mem['agent_id']) == str(agent_id)

        # 4. Test retrieving similar memories
        print("\n--- Testing vector similarity search ---")
        similar_memories = await memory_manager.retrieve_similar_memories(
            query="A test about database integration", 
            limit=5,
            similarity_threshold=0.1 # Lower threshold for fallback embedding
        )
        print(f"Retrieved similar memories count: {len(similar_memories)}")
        assert len(similar_memories) > 0
        for mem in similar_memories:
            print(f"  - Similarity: {mem['similarity']:.4f}, Content: '{mem['content'][:30]}...'")

        # 5. Test getting memory stats
        print("\n--- Testing memory stats ---")
        stats = await memory_manager.get_memory_stats()
        print(f"Memory stats: {stats}")
        assert stats['total_memories'] >= 1
        assert stats['total_embeddings'] >= 1
        assert stats['memory_types']['test'] >= 1

        # 6. Test deleting a memory
        print("\n--- Testing memory deletion ---")
        mem_to_delete = await memory_manager.retrieve_memories(query="vector DB", memory_type="test")
        if mem_to_delete:
            memory_id_to_delete = mem_to_delete[0]['id']
            deleted = await memory_manager.delete_memory(memory_id_to_delete)
            print(f"Deletion status for memory {memory_id_to_delete}: {deleted}")
            assert deleted
            
            retrieved_after_delete = await memory_manager.retrieve_memories(query="vector DB", memory_type="test")
            print(f"Retrieved memories count after deletion: {len(retrieved_after_delete)}")
            assert len(retrieved_after_delete) == 0

        # 7. Final cleanup
        print("\n--- Final cleanup ---")
        # Delete the dummy agent
        await session.delete(test_agent)
        await session.commit()
        print("Cleaned up dummy agent.")

if __name__ == "__main__":
    asyncio.run(test_memory_manager())
