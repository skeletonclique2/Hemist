#!/usr/bin/env python3
"""
Test script for Day 2: Agent Framework & State Management
Tests all core components: state machine, base agent, memory manager, communication, and orchestrator
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_state_machine():
    """Test the LangGraph state machine"""
    print("🧪 Testing State Machine...")
    
    try:
        from app.core import WorkflowStateMachine, WorkflowContext, WorkflowState
        
        # Create state machine
        sm = WorkflowStateMachine()
        print("✅ State machine created successfully")
        
        # Test workflow execution
        result = await sm.execute_workflow("AI Agents in 2024", 1000, 0.8)
        print(f"✅ Workflow executed: {result.current_state}")
        print(f"   - Research sources: {len(result.research_sources)}")
        print(f"   - Key insights: {len(result.key_insights)}")
        print(f"   - Draft content: {len(result.draft_content)} words")
        print(f"   - Final content: {len(result.final_content)} words")
        print(f"   - Quality score: {result.quality_score}")
        
        return True
        
    except Exception as e:
        print(f"❌ State machine test failed: {e}")
        return False

async def test_base_agent():
    """Test the base agent class"""
    print("\n🧪 Testing Base Agent...")
    
    try:
        from app.core import BaseAgent, AgentStatus, AgentType
        
        # Create a test agent (we'll need to implement the abstract method)
        class TestAgent(BaseAgent):
            async def execute(self, context):
                return {"result": "test completed", "agent": self.name}
        
        # Create agent
        agent = TestAgent(str(uuid.uuid4()), AgentType.RESEARCHER, "Test Researcher")
        print("✅ Test agent created successfully")
        
        # Test initialization
        success = await agent.initialize({"test_config": "value"})
        print(f"✅ Agent initialization: {success}")
        
        # Test task lifecycle
        await agent.start_task("Test research task")
        print(f"✅ Task started: {agent.state.current_task}")
        
        await agent.update_progress(0.5, "Halfway done")
        print(f"✅ Progress updated: {agent.state.task_progress:.1%}")
        
        await agent.complete_task({"result": "success"})
        print(f"✅ Task completed: {agent.state.status}")
        
        # Test memory
        memory_id = await agent.store_memory("Test memory content", "test", 0.8)
        print(f"✅ Memory stored: {memory_id}")
        
        memories = await agent.retrieve_memories("test")
        print(f"✅ Memories retrieved: {len(memories)}")
        
        # Test status
        status = agent.get_status()
        print(f"✅ Agent status: {status['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Base agent test failed: {e}")
        return False

async def test_memory_manager():
    """Test the memory manager"""
    print("\n🧪 Testing Memory Manager...")
    
    try:
        from app.core import MemoryManager
        
        # Create memory manager
        mm = MemoryManager()
        print("✅ Memory manager created successfully")
        
        # Test memory storage
        memory_id = await mm.store_memory(
            "This is a test memory about AI agents",
            "test",
            0.9,
            {"source": "test_script"}
        )
        print(f"✅ Memory stored: {memory_id}")
        
        # Test memory retrieval
        memory = await mm.get_memory(memory_id)
        print(f"✅ Memory retrieved: {memory['content'][:50]}...")
        
        # Test memory search
        search_results = await mm.search_memories("AI agents")
        print(f"✅ Memory search: {len(search_results)} results")
        
        # Test memory stats
        stats = await mm.get_memory_stats()
        print(f"✅ Memory stats: {stats['total_memories']} memories")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory manager test failed: {e}")
        return False

async def test_communication_hub():
    """Test the communication hub"""
    print("\n🧪 Testing Communication Hub...")
    
    try:
        from app.core import AgentCommunicationHub, AgentMessage, MessageType, MessagePriority
        
        # Create communication hub
        hub = AgentCommunicationHub()
        print("✅ Communication hub created successfully")
        
        # Test agent registration
        success = await hub.register_agent("test_agent_1", "Test Agent 1")
        print(f"✅ Agent registration: {success}")
        
        # Test message sending
        message = AgentMessage(
            sender_id="test_agent_1",
            recipient_id="test_agent_1",  # Send to self for testing
            message_type=MessageType.STATUS_UPDATE,
            priority=MessagePriority.NORMAL,
            content={"status": "testing"}
        )
        
        sent = await hub.send_message(message)
        print(f"✅ Message sent: {sent}")
        
        # Test message retrieval
        messages = await hub.get_messages("test_agent_1")
        print(f"✅ Messages retrieved: {len(messages)}")
        
        # Test hub status
        status = hub.get_hub_status()
        print(f"✅ Hub status: {status['registered_agents']} agents")
        
        return True
        
    except Exception as e:
        print(f"❌ Communication hub test failed: {e}")
        return False

async def test_workflow_orchestrator():
    """Test the workflow orchestrator"""
    print("\n🧪 Testing Workflow Orchestrator...")
    
    try:
        from app.core import WorkflowOrchestrator, BaseAgent, AgentType
        
        # Create orchestrator
        orchestrator = WorkflowOrchestrator()
        print("✅ Workflow orchestrator created successfully")
        
        # Test orchestrator start
        await orchestrator.start()
        print("✅ Orchestrator started")
        
        # Test workflow execution
        execution_id = await orchestrator.execute_workflow("Test Topic", 500, 0.7)
        print(f"✅ Workflow execution started: {execution_id}")
        
        # Wait a bit for workflow to process
        await asyncio.sleep(2)
        
        # Test workflow status
        status = await orchestrator.get_workflow_status(execution_id)
        print(f"✅ Workflow status: {status['status']}")
        
        # Test orchestrator status
        orch_status = orchestrator.get_orchestrator_status()
        print(f"✅ Orchestrator status: {orch_status['status']}")
        
        # Test orchestrator stop
        await orchestrator.stop()
        print("✅ Orchestrator stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow orchestrator test failed: {e}")
        return False

async def main():
    """Run all Day 2 foundation tests"""
    print("🚀 Day 2: Agent Framework & State Management Tests")
    print("=" * 60)
    
    tests = [
        ("State Machine", test_state_machine),
        ("Base Agent", test_base_agent),
        ("Memory Manager", test_memory_manager),
        ("Communication Hub", test_communication_hub),
        ("Workflow Orchestrator", test_workflow_orchestrator)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Day 2 Foundation Test Results")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Day 2 foundation tests passed! Ready for Day 3.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 