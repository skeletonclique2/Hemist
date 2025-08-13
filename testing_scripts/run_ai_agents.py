#!/usr/bin/env python3
"""
AI Agents System - Command Line Interface
Run and test the complete AI Agents system
"""

import asyncio
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env at the very start
load_dotenv()

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def run_content_generation_workflow(topic: str, target_length: int = 1200, 
                                        writing_style: str = "professional", 
                                        target_quality: float = 0.85):
    """Run a complete content generation workflow"""
    try:
        from app.agents.coordinator import CoordinatorAgent
        
        print(f"🚀 Starting content generation workflow...")
        print(f"📝 Topic: {topic}")
        print(f"📏 Target Length: {target_length} words")
        print(f"✍️  Writing Style: {writing_style}")
        print(f"🎯 Target Quality: {target_quality}")
        print("-" * 50)
        
        # Create coordinator agent
        coordinator = CoordinatorAgent("coordinator_cli", "CLI Coordinator")
        
        # Prepare workflow context
        context = {
            "topic": topic,
            "target_length": target_length,
            "writing_style": writing_style,
            "target_quality": target_quality,
            "research_depth": "comprehensive"
        }
        
        # Execute workflow
        result = await coordinator.execute(context)
        
        if result.get("status") == "success":
            print("\n✅ Workflow completed successfully!")
            print("=" * 50)
            
            # Show results
            workflow_summary = result.get("workflow_summary", {})
            
            # Research phase
            research = workflow_summary.get("research_phase", {})
            print(f"📚 Research Phase: {research.get('insights_count', 0)} insights, {research.get('sources_count', 0)} sources")
            
            # Writing phase
            writing = workflow_summary.get("writing_phase", {})
            print(f"✍️  Writing Phase: {writing.get('word_count', 0)} words, Quality: {writing.get('writing_quality', 0):.2f}")
            
            # Editing phase
            editing = workflow_summary.get("editing_phase", {})
            print(f"🔍 Editing Phase: Final Quality: {editing.get('final_quality', 0):.2f}")
            
            # Final content
            final_content = result.get("final_content", "")
            if final_content:
                print(f"\n📄 Final Content ({len(final_content)} characters):")
                print("-" * 30)
                print(final_content[:500] + "..." if len(final_content) > 500 else final_content)
            
            # Save to file
            output_file = f"output_{topic.replace(' ', '_').lower()}.md"
            with open(output_file, 'w') as f:
                f.write(f"# {topic}\n\n")
                f.write(f"**Generated:** {result.get('workflow_metadata', {}).get('completed_at', 'Unknown')}\n")
                f.write(f"**Quality Score:** {result.get('final_quality', 0):.2f}\n")
                f.write(f"**Word Count:** {writing.get('word_count', 0)}\n\n")
                f.write(final_content)
            
            print(f"\n💾 Content saved to: {output_file}")
            
        else:
            print(f"\n❌ Workflow failed: {result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_individual_agents():
    """Test individual agents"""
    try:
        print("🧪 Testing Individual Agents...")
        print("=" * 40)
        
        # Test Research Agent
        print("\n🔍 Testing Research Agent...")
        from app.agents.researcher import ResearchAgent
        researcher = ResearchAgent("test_researcher", "Test Researcher")
        research_result = await researcher.execute({
            "topic": "AI in Healthcare",
            "depth": "basic",
            "max_sources": 3
        })
        print(f"   Research: {'✅' if research_result.get('status') == 'success' else '❌'}")
        
        # Test Writer Agent
        print("\n✍️  Testing Writer Agent...")
        from app.agents.writer import WriterAgent
        writer = WriterAgent("test_writer", "Test Writer")
        writing_result = await writer.execute({
            "topic": "AI in Healthcare",
            "target_length": 500,
            "writing_style": "professional"
        })
        print(f"   Writing: {'✅' if writing_result.get('status') == 'success' else '❌'}")
        
        # Test Editor Agent
        print("\n🔍 Testing Editor Agent...")
        from app.agents.editor import EditorAgent
        editor = EditorAgent("test_editor", "Test Editor")
        editing_result = await editor.execute({
            "content": "AI is transforming healthcare through machine learning and automation.",
            "topic": "AI in Healthcare",
            "target_quality": 0.8
        })
        print(f"   Editing: {'✅' if editing_result.get('status') == 'success' else '❌'}")
        
        # Test Memory Agent
        print("\n🧠 Testing Memory Agent...")
        from app.agents.memory import MemoryAgent
        memory_agent = MemoryAgent("test_memory", "Test Memory")
        memory_result = await memory_agent.execute({
            "operation": "store",
            "content": "Test memory content",
            "memory_type": "test",
            "importance": 0.7
        })
        print(f"   Memory: {'✅' if memory_result.get('status') == 'success' else '❌'}")
        
        print("\n✅ All agent tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Agent testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def show_system_status():
    """Show system status and statistics"""
    try:
        print("📊 AI Agents System Status")
        print("=" * 30)
        
        # Check workflow persistence
        from app.core import WorkflowPersistence
        persistence = WorkflowPersistence()
        stats = await persistence.get_workflow_statistics()
        
        print(f"📁 Storage Path: {stats.get('storage_path', 'Unknown')}")
        print(f"🔄 Active Workflows: {stats.get('active', 0)}")
        print(f"✅ Completed Workflows: {stats.get('completed', 0)}")
        print(f"❌ Failed Workflows: {stats.get('failed', 0)}")
        print(f"📦 Archived Workflows: {stats.get('archived', 0)}")
        print(f"📈 Total Workflows: {stats.get('total', 0)}")
        
        # Check recent workflows
        recent_workflows = await persistence.list_workflows()
        if recent_workflows:
            print(f"\n🕒 Recent Workflows:")
            for workflow in recent_workflows[:5]:  # Show last 5
                workflow_id = workflow.get("workflow_id", "Unknown")
                status = workflow.get("status", "Unknown")
                saved_at = workflow.get("saved_at", "Unknown")
                print(f"   {workflow_id[:8]}... - {status} - {saved_at[:19]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

async def interactive_mode():
    """Run in interactive mode"""
    print("🎮 AI Agents System - Interactive Mode")
    print("=" * 40)
    print("Available commands:")
    print("  generate <topic> - Generate content on a topic")
    print("  test - Test individual agents")
    print("  status - Show system status")
    print("  help - Show this help")
    print("  quit - Exit the system")
    print("-" * 40)
    
    while True:
        try:
            # Check if running in an interactive terminal
            if not sys.stdin.isatty():
                print("Non-interactive mode detected. Exiting.")
                break
            
            command = input("\n🤖 Enter command: ").strip().lower()
            
            if command == "quit" or command == "exit":
                print("👋 Goodbye!")
                break
            elif command == "help":
                print("Available commands:")
                print("  generate <topic> - Generate content on a topic")
                print("  test - Test individual agents")
                print("  status - Show system status")
                print("  help - Show this help")
                print("  quit - Exit the system")
            elif command == "test":
                await test_individual_agents()
            elif command == "status":
                await show_system_status()
            elif command.startswith("generate "):
                topic = command[9:].strip()
                if topic:
                    await run_content_generation_workflow(topic)
                else:
                    print("❌ Please provide a topic: generate <topic>")
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="AI Agents System CLI")
    parser.add_argument("--topic", "-t", help="Topic for content generation")
    parser.add_argument("--length", "-l", type=int, default=1200, help="Target word count")
    parser.add_argument("--style", "-s", default="professional", help="Writing style")
    parser.add_argument("--quality", "-q", type=float, default=0.85, help="Target quality (0.0-1.0)")
    parser.add_argument("--test", action="store_true", help="Test individual agents")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # No longer set a default OPENAI_API_KEY; rely on .env and user environment
    
    if args.interactive:
        asyncio.run(interactive_mode())
    elif args.topic:
        asyncio.run(run_content_generation_workflow(
            args.topic, args.length, args.style, args.quality
        ))
    elif args.test:
        asyncio.run(test_individual_agents())
    elif args.status:
        asyncio.run(show_system_status())
    else:
        print("AI Agents System CLI")
        print("Use --help for available options")
        print("Or use --interactive for interactive mode")

if __name__ == "__main__":
    main()
