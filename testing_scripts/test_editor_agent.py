#!/usr/bin/env python3
"""
Test script for Editor Agent
Tests the Editor Agent and Editing Tools functionality
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_editing_tools():
    """Test EditingTools functionality"""
    print("🧪 Testing EditingTools...")
    
    try:
        from app.agents.editor.tools import EditingTools
        
        tools = EditingTools()
        print("✅ EditingTools initialized successfully")
        
        # Test content quality analysis
        content = """
        Artificial Intelligence in Healthcare
        
        AI is transforming healthcare in many ways. Machine learning algorithms can analyze medical images 
        to detect diseases with high accuracy. These systems help doctors make better decisions and improve 
        patient outcomes. The technology is becoming more accessible and affordable.
        
        However, there are challenges. Privacy concerns exist around patient data. Regulatory compliance 
        is complex. Integration with existing systems can be difficult.
        
        The future looks promising. AI will continue to advance and become more integrated into healthcare.
        """
        
        topic = "Artificial Intelligence in Healthcare"
        quality_metrics = await tools.analyze_content_quality(content, topic)
        print(f"✅ Content quality analysis completed")
        print(f"   Readability score: {quality_metrics.get('readability_score', 0):.2f}")
        print(f"   Topic relevance: {quality_metrics.get('topic_relevance', 0):.2f}")
        print(f"   Structure quality: {quality_metrics.get('structure_quality', 0):.2f}")
        
        # Test fact-checking
        research_data = {
            "insights": [
                "AI improves diagnostic accuracy by 20%",
                "Machine learning reduces treatment costs",
                "Privacy concerns exist in healthcare AI"
            ],
            "sources": [
                {"url": "example.com", "title": "AI Healthcare Study"}
            ]
        }
        
        fact_check_result = await tools.fact_check_content(content, research_data)
        print(f"✅ Fact-check completed: {fact_check_result.get('accuracy_score', 0):.2f} accuracy")
        
        # Test content improvement
        improved_content = await tools.improve_content_structure(content, quality_metrics)
        print(f"✅ Content structure improved: {len(improved_content)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ EditingTools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_editor_agent():
    """Test EditorAgent functionality"""
    print("\n🧪 Testing EditorAgent...")
    
    try:
        from app.agents.editor import EditorAgent
        from app.core import AgentType
        
        # Create editor agent
        agent = EditorAgent("editor_001", "Test Editor")
        print("✅ EditorAgent created successfully")
        
        # Test agent initialization
        print(f"   Agent ID: {agent.agent_id}")
        print(f"   Agent Type: {agent.agent_type}")
        print(f"   Agent Name: {agent.name}")
        print(f"   OpenAI Client: {'Available' if agent.openai_client else 'Not available (fallback mode)'}")
        
        # Test content analysis
        content = """
        # AI in Healthcare
        
        ## Introduction
        Artificial Intelligence is revolutionizing healthcare.
        
        ## Main Content
        AI helps with diagnosis and treatment planning.
        
        ## Conclusion
        The future of healthcare is AI-powered.
        """
        
        research_data = {
            "insights": ["AI improves diagnosis", "Machine learning helps treatment"],
            "sources": [{"url": "example.com", "title": "AI Study"}]
        }
        
        analysis_result = await agent._analyze_content_quality("AI in Healthcare", content, research_data)
        print(f"✅ Content quality analysis: {analysis_result.get('overall_quality', 0):.2f}")
        
        # Test fact-checking
        fact_check_result = await agent._fact_check_content(content, research_data)
        print(f"✅ Fact-check completed: {fact_check_result.get('accuracy_score', 0):.2f}")
        
        # Test content editing
        edited_content = await agent._edit_content(content, analysis_result, fact_check_result, "comprehensive")
        print(f"✅ Content editing completed: {len(edited_content)} characters")
        
        # Test final quality review
        final_quality = await agent._final_quality_review(edited_content, "AI in Healthcare", research_data)
        print(f"✅ Final quality review: {final_quality:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ EditorAgent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_editor_agent_execution():
    """Test full EditorAgent execution workflow"""
    print("\n🧪 Testing EditorAgent execution workflow...")
    
    try:
        from app.agents.editor import EditorAgent
        
        # Create editor agent
        agent = EditorAgent("editor_002", "Workflow Editor")
        
        # Test context
        context = {
            "content": """
            # The Future of Renewable Energy
            
            Solar power is the best energy source. It provides 100% of our energy needs and costs nothing.
            Wind energy is also good but not as good as solar. Nuclear power is dangerous and should be banned.
            
            The future is bright for renewable energy. Everyone should switch to solar panels immediately.
            """,
            "topic": "The Future of Renewable Energy",
            "research_data": {
                "insights": [
                    "Solar power costs have decreased significantly",
                    "Wind energy is becoming competitive",
                    "Nuclear power has safety considerations",
                    "Renewable energy adoption is increasing"
                ],
                "sources": [
                    {"url": "energy.gov", "title": "Renewable Energy Report 2024"},
                    {"url": "iea.org", "title": "Global Energy Outlook"}
                ]
            },
            "target_quality": 0.9,
            "editing_style": "comprehensive"
        }
        
        # Execute editing task
        print("   Starting editing execution...")
        result = await agent.execute(context)
        
        if result.get("status") == "success":
            print("✅ Editing execution completed successfully")
            print(f"   Topic: {result.get('topic')}")
            print(f"   Original length: {result.get('original_content_length')}")
            print(f"   Edited length: {result.get('edited_content_length')}")
            print(f"   Quality score: {result.get('quality_score', 0):.2f}")
            print(f"   Improvements made: {result.get('improvements_made')}")
            
            # Show editing report summary
            editing_report = result.get('editing_report', {})
            if editing_report:
                summary = editing_report.get('editing_summary', {})
                print(f"   Quality improvement: {summary.get('quality_improvement', 0):.2f}")
                print(f"   Editing style: {summary.get('editing_style')}")
            
        else:
            print(f"❌ Editing execution failed: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ EditorAgent execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_section_review():
    """Test specific section review functionality"""
    print("\n🧪 Testing Section Review...")
    
    try:
        from app.agents.editor import EditorAgent
        
        # Create editor agent
        agent = EditorAgent("editor_003", "Section Reviewer")
        
        # Test content with sections
        content = """
        # AI in Healthcare
        
        ## Introduction
        Artificial Intelligence is transforming healthcare delivery and improving patient outcomes.
        
        ## Main Benefits
        AI helps doctors diagnose diseases faster and more accurately than traditional methods.
        
        ## Challenges
        Privacy concerns and regulatory compliance issues exist.
        
        ## Conclusion
        The future of healthcare is increasingly AI-powered.
        """
        
        research_data = {
            "insights": ["AI improves diagnosis", "Privacy concerns exist"],
            "sources": [{"url": "example.com", "title": "AI Study"}]
        }
        
        # Review specific section
        section_review = await agent.review_specific_section(content, "Main Benefits", research_data)
        
        if "error" not in section_review:
            print("✅ Section review completed successfully")
            print(f"   Section: {section_review.get('section')}")
            print(f"   Quality analysis: {section_review.get('quality_analysis', {})}")
            print(f"   Fact check: {section_review.get('fact_check', {})}")
            print(f"   Recommendations: {len(section_review.get('recommendations', []))}")
            return True
        else:
            print(f"❌ Section review failed: {section_review.get('error')}")
            return False
        
    except Exception as e:
        print(f"❌ Section review test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Editor Agent Tests\n")
    
    # Test 1: Editing Tools
    tools_success = await test_editing_tools()
    
    # Test 2: Editor Agent Basic
    agent_success = await test_editor_agent()
    
    # Test 3: Editor Agent Execution
    execution_success = await test_editor_agent_execution()
    
    # Test 4: Section Review
    section_review_success = await test_section_review()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    print(f"Editing Tools: {'✅ PASSED' if tools_success else '❌ FAILED'}")
    print(f"Editor Agent: {'✅ PASSED' if agent_success else '❌ FAILED'}")
    print(f"Execution Workflow: {'✅ PASSED' if execution_success else '❌ FAILED'}")
    print(f"Section Review: {'✅ PASSED' if section_review_success else '❌ FAILED'}")
    
    if all([tools_success, agent_success, execution_success, section_review_success]):
        print("\n🎉 ALL TESTS PASSED! Editor Agent is working correctly.")
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