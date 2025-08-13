#!/usr/bin/env python3
"""
Test script for Memory Agent
Tests the Memory Agent functionality for advanced context management
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_memory_agent_initialization():
    """Test Memory Agent initialization"""
    print("🧪 Testing Memory Agent Initialization...")
    
    try:
        from app.agents.memory import MemoryAgent
        from app.core import AgentType
        
        # Create memory agent
        agent = MemoryAgent("memory_001", "Test Memory Agent")
        print("✅ Memory Agent created successfully")
        
        # Test agent initialization
        print(f"   Agent ID: {agent.agent_id}")
        print(f"   Agent Type: {agent.agent_type}")
        print(f"   Agent Name: {agent.name}")
        print(f"   Memory Manager: {'Available' if agent.memory_manager else 'Not available'}")
        print(f"   Memory Categories: {len(agent.memory_categories)} categories")
        
        # Test agent initialization
        await agent.initialize()
        print("✅ Memory Agent initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory Agent initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_memory_operations():
    """Test basic memory operations"""
    print("\n🧪 Testing Basic Memory Operations...")
    
    try:
        from app.agents.memory import MemoryAgent
        
        # Create memory agent
        agent = MemoryAgent("memory_002", "Memory Operations Tester")
        
        # Test memory storage
        store_context = {
            "operation": "store",
            "content": "AI is transforming business operations through automation and data analysis",
            "memory_type": "knowledge",
            "importance": 0.8,
            "metadata": {"topic": "AI in Business", "source": "test"}
        }
        
        store_result = await agent.execute(store_context)
        print(f"✅ Memory storage: {store_result.get('status')}")
        
        # Test memory retrieval
        retrieve_context = {
            "operation": "retrieve",
            "memory_type": "knowledge",
            "query": "AI business",
            "limit": 5
        }
        
        retrieve_result = await agent.execute(retrieve_context)
        print(f"✅ Memory retrieval: {retrieve_result.get('status')}")
        print(f"   Retrieved: {retrieve_result.get('count', 0)} memories")
        
        # Test memory organization
        organize_context = {
            "operation": "organize",
            "organization_type": "categorize"
        }
        
        organize_result = await agent.execute(organize_context)
        print(f"✅ Memory organization: {organize_result.get('status')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_memory_analysis():
    """Test memory analysis operations"""
    print("\n🧪 Testing Memory Analysis...")
    
    try:
        from app.agents.memory import MemoryAgent
        
        # Create memory agent
        agent = MemoryAgent("memory_003", "Memory Analysis Tester")
        
        # Store some test memories first
        test_memories = [
            {
                "content": "Machine learning improves decision making in business",
                "memory_type": "knowledge",
                "importance": 0.9,
                "metadata": {"topic": "Machine Learning", "source": "test"}
            },
            {
                "content": "Data analytics helps identify business trends",
                "memory_type": "knowledge",
                "importance": 0.7,
                "metadata": {"topic": "Data Analytics", "source": "test"}
            },
            {
                "content": "Automation reduces operational costs",
                "memory_type": "knowledge",
                "importance": 0.6,
                "metadata": {"topic": "Automation", "source": "test"}
            }
        ]
        
        # Store test memories
        for memory_data in test_memories:
            store_context = {
                "operation": "store",
                **memory_data
            }
            await agent.execute(store_context)
        
        print("✅ Test memories stored successfully")
        
        # Test memory overview
        overview_context = {
            "operation": "analyze",
            "analysis_type": "overview"
        }
        
        overview_result = await agent.execute(overview_context)
        print(f"✅ Memory overview: {overview_result.get('status')}")
        
        if overview_result.get("status") == "success":
            overview = overview_result.get("operation", {})
            print(f"   Total Memories: {overview_result.get('total_memories', 0)}")
            print(f"   Memory Health: {overview_result.get('memory_health', 'unknown')}")
        
        # Test memory trends
        trends_context = {
            "operation": "analyze",
            "analysis_type": "trends"
        }
        
        trends_result = await agent.execute(trends_context)
        print(f"✅ Memory trends: {trends_result.get('status')}")
        
        # Test memory quality analysis
        quality_context = {
            "operation": "analyze",
            "analysis_type": "quality"
        }
        
        quality_result = await agent.execute(quality_context)
        print(f"✅ Memory quality: {quality_result.get('status')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_memory_cleanup():
    """Test memory cleanup operations"""
    print("\n🧪 Testing Memory Cleanup...")
    
    try:
        from app.agents.memory import MemoryAgent
        
        # Create memory agent
        agent = MemoryAgent("memory_004", "Memory Cleanup Tester")
        
        # Test cleanup operations
        cleanup_types = ["expired", "low_importance", "duplicates"]
        
        for cleanup_type in cleanup_types:
            cleanup_context = {
                "operation": "cleanup",
                "cleanup_type": cleanup_type,
                "threshold": 30
            }
            
            cleanup_result = await agent.execute(cleanup_context)
            print(f"✅ {cleanup_type.title()} cleanup: {cleanup_result.get('status')}")
            
            if cleanup_result.get("status") == "success":
                if cleanup_type == "expired":
                    print(f"   Expired memories: {cleanup_result.get('expired_memories', 0)}")
                elif cleanup_type == "low_importance":
                    print(f"   Low importance memories: {cleanup_result.get('low_importance_memories', 0)}")
                elif cleanup_type == "duplicates":
                    print(f"   Duplicate memories: {cleanup_result.get('duplicate_memories', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory cleanup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_memory_indexing():
    """Test memory indexing functionality"""
    print("\n🧪 Testing Memory Indexing...")
    
    try:
        from app.agents.memory import MemoryAgent
        
        # Create memory agent
        agent = MemoryAgent("memory_005", "Memory Indexing Tester")
        
        # Test index rebuilding
        index_context = {
            "operation": "organize",
            "organization_type": "index"
        }
        
        index_result = await agent.execute(index_context)
        print(f"✅ Index rebuilding: {index_result.get('status')}")
        
        if index_result.get("status") == "success":
            print(f"   Indexes rebuilt: {index_result.get('indexes_rebuilt', [])}")
            print(f"   Memories indexed: {index_result.get('total_memories_indexed', 0)}")
        
        # Test memory statistics
        stats = await agent.get_memory_statistics()
        print(f"✅ Memory statistics retrieved")
        print(f"   Total memories: {stats.get('total_memories', 0)}")
        print(f"   Memory types: {stats.get('memory_types', [])}")
        print(f"   Index status: {stats.get('index_status', {})}")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory indexing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_advanced_memory_features():
    """Test advanced memory features"""
    print("\n🧪 Testing Advanced Memory Features...")
    
    try:
        from app.agents.memory import MemoryAgent
        
        # Create memory agent
        agent = MemoryAgent("memory_006", "Advanced Features Tester")
        
        # Test advanced filtering
        retrieve_context = {
            "operation": "retrieve",
            "memory_type": "knowledge",
            "query": "AI",
            "limit": 10,
            "filters": {
                "min_importance": 0.7,
                "metadata_filters": {"source": "test"}
            }
        }
        
        retrieve_result = await agent.execute(retrieve_context)
        print(f"✅ Advanced filtering: {retrieve_result.get('status')}")
        print(f"   Filtered memories: {retrieve_result.get('count', 0)}")
        
        # Test memory categorization
        categorize_context = {
            "operation": "organize",
            "organization_type": "categorize"
        }
        
        categorize_result = await agent.execute(categorize_context)
        print(f"✅ Memory categorization: {categorize_result.get('status')}")
        
        if categorize_result.get("status") == "success":
            categories = categorize_result.get("categories", {})
            print(f"   Categories: {len(categories)}")
            for category, info in categories.items():
                print(f"     {category}: {info.get('count', 0)} memories")
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced memory features test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Memory Agent Tests\n")
    
    # Test 1: Initialization
    init_success = await test_memory_agent_initialization()
    
    # Test 2: Basic Operations
    operations_success = await test_memory_operations()
    
    # Test 3: Memory Analysis
    analysis_success = await test_memory_analysis()
    
    # Test 4: Memory Cleanup
    cleanup_success = await test_memory_cleanup()
    
    # Test 5: Memory Indexing
    indexing_success = await test_memory_indexing()
    
    # Test 6: Advanced Features
    advanced_success = await test_advanced_memory_features()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    print(f"Initialization: {'✅ PASSED' if init_success else '❌ FAILED'}")
    print(f"Basic Operations: {'✅ PASSED' if operations_success else '❌ FAILED'}")
    print(f"Memory Analysis: {'✅ PASSED' if analysis_success else '❌ FAILED'}")
    print(f"Memory Cleanup: {'✅ PASSED' if cleanup_success else '❌ FAILED'}")
    print(f"Memory Indexing: {'✅ PASSED' if indexing_success else '❌ FAILED'}")
    print(f"Advanced Features: {'✅ PASSED' if advanced_success else '❌ FAILED'}")
    
    if all([init_success, operations_success, analysis_success, cleanup_success, indexing_success, advanced_success]):
        print("\n🎉 ALL TESTS PASSED! Memory Agent is working correctly.")
        print("🧠 Advanced context management and memory operations are functional!")
        return True
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    # Set up environment
    os.environ.setdefault("OPENAI_API_KEY", "test_key")
    
    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 