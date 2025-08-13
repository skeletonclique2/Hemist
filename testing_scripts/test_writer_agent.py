#!/usr/bin/env python3
"""
Test script for Writer Agent
Tests the Writer Agent and Writing Tools functionality
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_writing_tools():
    """Test WritingTools functionality"""
    print("🧪 Testing WritingTools...")
    
    try:
        from app.agents.writer.tools import WritingTools
        
        tools = WritingTools()
        print("✅ WritingTools initialized successfully")
        
        # Test content structure creation
        topic = "Artificial Intelligence in Healthcare"
        target_length = 1500
        insights = [
            "AI improves diagnostic accuracy",
            "Machine learning reduces treatment costs",
            "Predictive analytics enhance patient outcomes",
            "Natural language processing streamlines documentation",
            "Computer vision aids in medical imaging"
        ]
        sources = [{"url": "example.com", "title": "AI Healthcare Study"}]
        
        structure = await tools.create_content_structure(topic, target_length, insights, sources)
        print(f"✅ Content structure created: {len(structure.get('sections', []))} sections")
        print(f"   Target length: {structure.get('target_length')} words")
        print(f"   Estimated reading time: {structure.get('estimated_reading_time')}")
        
        # Test section content generation
        section = structure['sections'][0]  # Introduction
        content = await tools.generate_section_content(topic, section, {"insights": insights}, "professional")
        print(f"✅ Section content generated: {len(content)} characters")
        
        # Test content optimization
        optimized = await tools.optimize_content(content, 300, "professional")
        print(f"✅ Content optimized: {len(optimized)} characters")
        
        # Test content finalization
        finalized = await tools.finalize_content(optimized, topic, "professional")
        print(f"✅ Content finalized: {len(finalized)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ WritingTools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_writer_agent():
    """Test WriterAgent functionality"""
    print("\n🧪 Testing WriterAgent...")
    
    try:
        from app.agents.writer import WriterAgent
        from app.core import AgentType
        
        # Create writer agent
        agent = WriterAgent("writer_001", "Test Writer")
        print("✅ WriterAgent created successfully")
        
        # Test agent initialization
        print(f"   Agent ID: {agent.agent_id}")
        print(f"   Agent Type: {agent.agent_type}")
        print(f"   Agent Name: {agent.name}")
        print(f"   OpenAI Client: {'Available' if agent.openai_client else 'Not available (fallback mode)'}")
        
        # Test content planning
        research_data = {
            "insights": [
                "AI improves diagnostic accuracy by 20%",
                "Machine learning reduces treatment costs by 30%",
                "Predictive analytics enhance patient outcomes significantly"
            ],
            "sources": [
                {"url": "example1.com", "title": "AI Healthcare Study 2024"},
                {"url": "example2.com", "title": "ML Cost Analysis Report"}
            ]
        }
        
        content_plan = await agent._create_content_plan("AI in Healthcare", 1200, research_data)
        print(f"✅ Content plan created: {len(content_plan.get('sections', []))} sections")
        
        # Test fallback content generation
        fallback_content = await agent._generate_fallback_content(
            "AI in Healthcare", content_plan, research_data, "professional"
        )
        print(f"✅ Fallback content generated: {len(fallback_content)} characters")
        
        # Test content quality calculation
        quality_score = agent._calculate_content_quality(fallback_content, content_plan)
        print(f"✅ Content quality calculated: {quality_score:.2f}")
        
        # Test memory storage
        await agent._store_writing_results("AI in Healthcare", fallback_content, content_plan)
        print("✅ Writing results stored in memory")
        
        # Test writing history retrieval
        history = await agent.get_writing_history("AI in Healthcare")
        print(f"✅ Writing history retrieved: {len(history)} entries")
        
        return True
        
    except Exception as e:
        print(f"❌ WriterAgent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_writer_agent_execution():
    """Test full WriterAgent execution workflow"""
    print("\n🧪 Testing WriterAgent execution workflow...")
    
    try:
        from app.agents.writer import WriterAgent
        
        # Create writer agent
        agent = WriterAgent("writer_002", "Workflow Writer")
        
        # Test context
        context = {
            "topic": "The Future of Renewable Energy",
            "target_length": 1000,
            "research_data": {
                "insights": [
                    "Solar power costs have decreased by 90% in the last decade",
                    "Wind energy is now competitive with fossil fuels",
                    "Battery storage technology is advancing rapidly",
                    "Grid integration challenges remain significant"
                ],
                "sources": [
                    {"url": "energy.gov", "title": "Renewable Energy Report 2024"},
                    {"url": "iea.org", "title": "Global Energy Outlook"}
                ]
            },
            "writing_style": "professional"
        }
        
        # Execute writing task
        print("   Starting writing execution...")
        result = await agent.execute(context)
        
        if result.get("status") == "success":
            print("✅ Writing execution completed successfully")
            print(f"   Topic: {result.get('topic')}")
            print(f"   Word count: {result.get('word_count')}")
            print(f"   Writing style: {result.get('writing_style')}")
            print(f"   Quality score: {result.get('quality_score', 0):.2f}")
            
            # Show first 200 characters of content
            content = result.get('content', '')
            print(f"   Content preview: {content[:200]}...")
            
        else:
            print(f"❌ Writing execution failed: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ WriterAgent execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Writer Agent Tests\n")
    
    # Test 1: Writing Tools
    tools_success = await test_writing_tools()
    
    # Test 2: Writer Agent Basic
    agent_success = await test_writer_agent()
    
    # Test 3: Writer Agent Execution
    execution_success = await test_writer_agent_execution()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    print(f"Writing Tools: {'✅ PASSED' if tools_success else '❌ FAILED'}")
    print(f"Writer Agent: {'✅ PASSED' if agent_success else '❌ FAILED'}")
    print(f"Execution Workflow: {'✅ PASSED' if execution_success else '❌ FAILED'}")
    
    if all([tools_success, agent_success, execution_success]):
        print("\n🎉 ALL TESTS PASSED! Writer Agent is working correctly.")
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