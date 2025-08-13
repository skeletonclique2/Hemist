#!/usr/bin/env python3
"""
Test script for Coordinator Agent
Tests the complete end-to-end content generation workflow
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_coordinator_agent_initialization():
    """Test Coordinator Agent initialization"""
    print("🧪 Testing Coordinator Agent Initialization...")
    
    try:
        from app.agents.coordinator import CoordinatorAgent
        from app.core import AgentType
        
        # Create coordinator agent
        coordinator = CoordinatorAgent("coordinator_001", "Test Coordinator")
        print("✅ Coordinator Agent created successfully")
        
        # Test agent initialization
        print(f"   Agent ID: {coordinator.agent_id}")
        print(f"   Agent Type: {coordinator.agent_type}")
        print(f"   Agent Name: {coordinator.name}")
        print(f"   Communication Hub: {'Available' if coordinator.communication_hub else 'Not available'}")
        
        # Test agent initialization
        await coordinator.initialize()
        print("✅ Coordinator Agent initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Coordinator Agent initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_coordinator_agent_workflow():
    """Test the complete workflow orchestration"""
    print("\n🧪 Testing Complete Workflow Orchestration...")
    
    try:
        from app.agents.coordinator import CoordinatorAgent
        
        # Create coordinator agent
        coordinator = CoordinatorAgent("coordinator_002", "Workflow Coordinator")
        
        # Test workflow context
        context = {
            "topic": "The Impact of Artificial Intelligence on Modern Business",
            "target_length": 1200,
            "writing_style": "professional",
            "target_quality": 0.85,
            "research_depth": "comprehensive"
        }
        
        # Execute complete workflow
        print("   Starting complete workflow execution...")
        print(f"   Topic: {context['topic']}")
        print(f"   Target Length: {context['target_length']} words")
        print(f"   Writing Style: {context['writing_style']}")
        print(f"   Target Quality: {context['target_quality']}")
        
        result = await coordinator.execute(context)
        
        if result.get("status") == "success":
            print("✅ Complete workflow executed successfully!")
            
            # Show workflow summary
            workflow_summary = result.get("workflow_summary", {})
            
            # Research phase results
            research_phase = workflow_summary.get("research_phase", {})
            print(f"   📚 Research Phase: {research_phase.get('status')}")
            print(f"      Insights: {research_phase.get('insights_count', 0)}")
            print(f"      Sources: {research_phase.get('sources_count', 0)}")
            print(f"      Quality: {research_phase.get('research_quality', 0):.2f}")
            
            # Writing phase results
            writing_phase = workflow_summary.get("writing_phase", {})
            print(f"   ✍️  Writing Phase: {writing_phase.get('status')}")
            print(f"      Word Count: {writing_phase.get('word_count', 0)}")
            print(f"      Style: {writing_phase.get('writing_style')}")
            print(f"      Quality: {writing_phase.get('writing_quality', 0):.2f}")
            
            # Editing phase results
            editing_phase = workflow_summary.get("editing_phase", {})
            print(f"   🔍 Editing Phase: {editing_phase.get('status')}")
            print(f"      Final Quality: {editing_phase.get('final_quality', 0):.2f}")
            print(f"      Improvements: {editing_phase.get('improvements_made', 0)}")
            
            # Final results
            print(f"   🎯 Final Results:")
            print(f"      Content Length: {len(result.get('final_content', ''))} characters")
            print(f"      Overall Quality: {result.get('final_quality', 0):.2f}")
            
            # Workflow metadata
            metadata = result.get("workflow_metadata", {})
            print(f"      Workflow ID: {metadata.get('workflow_id', 'N/A')}")
            print(f"      Duration: {metadata.get('total_duration', 'N/A')}")
            
            # Show content preview
            content = result.get("final_content", "")
            if content:
                print(f"   📄 Content Preview:")
                print(f"      {content[:200]}...")
            
        else:
            print(f"❌ Workflow execution failed: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow orchestration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_coordinator_agent_controls():
    """Test workflow control functions"""
    print("\n🧪 Testing Workflow Controls...")
    
    try:
        from app.agents.coordinator import CoordinatorAgent
        
        # Create coordinator agent
        coordinator = CoordinatorAgent("coordinator_003", "Control Tester")
        
        # Test workflow status
        status = await coordinator.get_workflow_status()
        print("✅ Workflow status retrieved successfully")
        print(f"   Coordinator Status: {status.get('coordinator_status')}")
        print(f"   Agent Statuses: {status.get('agent_statuses')}")
        
        # Test performance metrics
        metrics = await coordinator.get_agent_performance_metrics()
        print("✅ Performance metrics retrieved successfully")
        print(f"   Metrics: {len(metrics)} agent metrics available")
        
        # Test workflow controls (these will be empty since no workflow is running)
        pause_result = await coordinator.pause_workflow()
        print(f"   Pause Workflow: {'Success' if pause_result else 'Failed (expected)'}")
        
        resume_result = await coordinator.resume_workflow()
        print(f"   Resume Workflow: {'Success' if resume_result else 'Failed (expected)'}")
        
        cancel_result = await coordinator.cancel_workflow()
        print(f"   Cancel Workflow: {'Success' if cancel_result else 'Failed (expected)'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow controls test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_coordinator_agent_memory():
    """Test memory and history functionality"""
    print("\n🧪 Testing Memory and History...")
    
    try:
        from app.agents.coordinator import CoordinatorAgent
        
        # Create coordinator agent
        coordinator = CoordinatorAgent("coordinator_004", "Memory Tester")
        
        # Test memory storage
        await coordinator.store_memory(
            "Test memory entry for coordinator",
            "test_memory",
            0.7,
            {"test": True, "agent": "coordinator"}
        )
        print("✅ Memory storage test completed")
        
        # Test memory retrieval
        memories = await coordinator.retrieve_memories(memory_type="test_memory")
        print(f"✅ Memory retrieval test completed: {len(memories)} memories found")
        
        # Test workflow history
        workflow_status = await coordinator.get_workflow_status()
        history = workflow_status.get("workflow_history", [])
        print(f"✅ Workflow history test completed: {len(history)} workflows in history")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory and history test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_coordinator_agent_cleanup():
    """Test cleanup functionality"""
    print("\n🧪 Testing Cleanup...")
    
    try:
        from app.agents.coordinator import CoordinatorAgent
        
        # Create coordinator agent
        coordinator = CoordinatorAgent("coordinator_005", "Cleanup Tester")
        
        # Test cleanup
        await coordinator.cleanup()
        print("✅ Cleanup test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Cleanup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Coordinator Agent Tests\n")
    
    # Test 1: Initialization
    init_success = await test_coordinator_agent_initialization()
    
    # Test 2: Complete Workflow
    workflow_success = await test_coordinator_agent_workflow()
    
    # Test 3: Workflow Controls
    controls_success = await test_coordinator_agent_controls()
    
    # Test 4: Memory and History
    memory_success = await test_coordinator_agent_memory()
    
    # Test 5: Cleanup
    cleanup_success = await test_coordinator_agent_cleanup()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    print(f"Initialization: {'✅ PASSED' if init_success else '❌ FAILED'}")
    print(f"Complete Workflow: {'✅ PASSED' if workflow_success else '❌ FAILED'}")
    print(f"Workflow Controls: {'✅ PASSED' if controls_success else '❌ FAILED'}")
    print(f"Memory & History: {'✅ PASSED' if memory_success else '❌ FAILED'}")
    print(f"Cleanup: {'✅ PASSED' if cleanup_success else '❌ FAILED'}")
    
    if all([init_success, workflow_success, controls_success, memory_success, cleanup_success]):
        print("\n🎉 ALL TESTS PASSED! Coordinator Agent is working correctly.")
        print("🎯 Complete end-to-end workflow orchestration is functional!")
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