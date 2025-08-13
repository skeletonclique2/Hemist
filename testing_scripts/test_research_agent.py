#!/usr/bin/env python3
"""
Test script for Research Agent
Tests research capabilities, content extraction, and insight generation
"""

import asyncio
import sys
import os
import uuid

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_research_agent():
    """Test the Research Agent functionality"""
    print("🧪 Testing Research Agent...")
    
    try:
        from app.agents import ResearchAgent
        
        # Create research agent
        agent_id = str(uuid.uuid4())
        agent = ResearchAgent(agent_id, "Test Research Agent")
        print("✅ Research agent created successfully")
        
        # Test initialization
        success = await agent.initialize()
        print(f"✅ Agent initialization: {success}")
        
        # Test research execution
        context = {
            "topic": "Artificial Intelligence in Healthcare",
            "target_length": 800,
            "quality_threshold": 0.8
        }
        
        print("🚀 Starting research execution...")
        result = await agent.execute(context)
        
        print(f"✅ Research completed: {result['status']}")
        print(f"   - Sources found: {result.get('sources_count', 0)}")
        print(f"   - Insights extracted: {result.get('insights_count', 0)}")
        print(f"   - Summary length: {result.get('summary_length', 0)} characters")
        print(f"   - Quality score: {result.get('quality_score', 0):.2f}")
        
        # Test memory retrieval
        memories = await agent.retrieve_memories(memory_type="research_overview")
        print(f"✅ Research memories stored: {len(memories)}")
        
        # Test research history
        history = await agent.get_research_history("Artificial Intelligence in Healthcare")
        print(f"✅ Research history retrieved: {len(history)} entries")
        
        return True
        
    except Exception as e:
        print(f"❌ Research agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_research_tools():
    """Test the Research Tools functionality"""
    print("\n🧪 Testing Research Tools...")
    
    try:
        from app.agents.researcher.tools import ResearchTools
        
        # Create research tools
        tools = ResearchTools()
        print("✅ Research tools created successfully")
        
        # Test web search (simulated)
        search_results = await tools.search_web("Machine Learning", max_results=5)
        print(f"✅ Web search: {len(search_results)} results")
        
        # Test content extraction (simulated URL)
        test_url = "https://example.com/test"
        content = await tools.extract_content(test_url)
        print(f"✅ Content extraction: {'Success' if content else 'Failed'}")
        
        # Test credibility assessment
        credibility = await tools.assess_credibility(test_url, "Sample content about machine learning")
        print(f"✅ Credibility assessment: {credibility['overall_assessment']} ({credibility['credibility_score']:.2f})")
        
        # Test source validation
        validation = await tools.validate_source(test_url)
        print(f"✅ Source validation: {validation['accessible']}")
        
        # Clean up
        await tools.close()
        print("✅ Research tools closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Research tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all Research Agent tests"""
    print("🚀 Research Agent Tests")
    print("=" * 50)
    
    tests = [
        ("Research Tools", test_research_tools),
        ("Research Agent", test_research_agent)
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
    print("\n" + "=" * 50)
    print("📊 Research Agent Test Results")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Research Agent tests passed! Ready for Writer Agent.")
        return True
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 