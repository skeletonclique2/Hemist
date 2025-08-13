# 🚀 AI Agents System - Complete Guide

A production-ready AI agent system for automated content generation, built with modern Python and async architecture.

## 🎯 What This System Does

This AI Agents System automatically generates high-quality content by orchestrating multiple specialized AI agents:

1. **🔍 Research Agent** - Conducts web research and gathers insights
2. **✍️ Writer Agent** - Creates well-structured content based on research
3. **🔍 Editor Agent** - Reviews, fact-checks, and improves content quality
4. **🧠 Memory Agent** - Manages context and knowledge persistence
5. **🎯 Coordinator Agent** - Orchestrates the entire workflow

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Activate virtual environment
source hem/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key (optional - system works without it)
export OPENAI_API_KEY="your_api_key_here"
```

### 2. Run the System

#### Interactive Mode (Recommended for testing)
```bash
python run_ai_agents.py --interactive
```

#### Generate Content on a Specific Topic
```bash
python run_ai_agents.py --topic "The Future of Artificial Intelligence" --length 1500 --style professional --quality 0.9
```

#### Test Individual Agents
```bash
python run_ai_agents.py --test
```

#### Check System Status
```bash
python run_ai_agents.py --status
```

## 🎮 Interactive Mode Commands

When running in interactive mode, you can use these commands:

```
🤖 Available commands:
  generate <topic> - Generate content on a topic
  test - Test individual agents
  status - Show system status
  help - Show this help
  quit - Exit the system

🤖 Enter command: generate AI in Healthcare
🤖 Enter command: test
🤖 Enter command: status
🤖 Enter command: quit
```

## 📝 Content Generation Examples

### Example 1: Professional Article
```bash
python run_ai_agents.py --topic "Machine Learning in Finance" --length 2000 --style professional --quality 0.9
```

### Example 2: Blog Post
```bash
python run_ai_agents.py --topic "Top 10 AI Trends 2024" --length 800 --style conversational --quality 0.8
```

### Example 3: Technical Report
```bash
python run_ai_agents.py --topic "Neural Network Architecture Comparison" --length 3000 --style academic --quality 0.95
```

## 🔧 Advanced Usage

### Custom Workflow Parameters

```python
from app.agents.coordinator import CoordinatorAgent

# Create coordinator
coordinator = CoordinatorAgent("my_coordinator", "Custom Coordinator")

# Custom workflow
context = {
    "topic": "Your Topic Here",
    "target_length": 1500,
    "writing_style": "professional",  # professional, conversational, academic
    "target_quality": 0.9,
    "research_depth": "comprehensive"  # basic, comprehensive
}

# Execute workflow
result = await coordinator.execute(context)
```

### Individual Agent Usage

```python
# Research Agent
from app.agents.researcher import ResearchAgent
researcher = ResearchAgent("researcher_001", "Research Specialist")
research_result = await researcher.execute({
    "topic": "Your Topic",
    "depth": "comprehensive",
    "max_sources": 10
})

# Writer Agent
from app.agents.writer import WriterAgent
writer = WriterAgent("writer_001", "Content Writer")
writing_result = await writer.execute({
    "topic": "Your Topic",
    "target_length": 1000,
    "writing_style": "professional"
})

# Editor Agent
from app.agents.editor import EditorAgent
editor = EditorAgent("editor_001", "Quality Editor")
editing_result = await editor.execute({
    "content": "Your content here",
    "topic": "Your Topic",
    "target_quality": 0.9
})
```

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Coordinator   │───▶│   Research      │───▶│   Writer        │
│     Agent       │    │     Agent       │    │     Agent       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Memory        │    │   Communication │    │   Workflow      │
│     Agent       │    │       Hub       │    │   Persistence   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Editor        │    │   State         │    │   Memory        │
│     Agent       │    │   Machine       │    │   Manager       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 What This System CAN Do

✅ **Content Generation**: Automatically research and write articles on any topic
✅ **Quality Control**: Fact-checking, editing, and quality improvement
✅ **Multiple Styles**: Professional, conversational, academic writing styles
✅ **Research Integration**: Web search, source analysis, and insight extraction
✅ **Memory Management**: Persistent knowledge storage and retrieval
✅ **Workflow Orchestration**: Coordinated multi-agent execution
✅ **State Persistence**: Save and resume workflows
✅ **Fallback Mechanisms**: Works without external API keys

## ❌ What This System CANNOT Do (Yet)

❌ **Publishing**: No automatic publishing to Medium, LinkedIn, etc.
❌ **Social Media**: No direct posting to social platforms
❌ **Messaging**: No WhatsApp, Telegram, Slack, or Discord integration
❌ **Real-time Communication**: No live chat or messaging capabilities

## 🔮 Future Enhancements (Roadmap)

### Phase 1: Publishing Integration
- Medium API integration for automatic publishing
- LinkedIn content scheduling
- WordPress/other CMS integration

### Phase 2: Social Media Automation
- Twitter/X posting
- Facebook page management
- Instagram content creation

### Phase 3: Communication Channels
- WhatsApp Business API integration
- Telegram bot functionality
- Slack workspace integration
- Discord bot capabilities

### Phase 4: Advanced Features
- Multi-language content generation
- Video script creation
- Podcast episode planning
- Email newsletter automation

## 🧪 Testing and Development

### Run All Tests
```bash
# Test individual components
python test_day2_foundation.py
python test_research_agent.py
python test_writer_agent.py
python test_editor_agent.py
python test_coordinator_agent.py
python test_memory_agent.py
```

### Development Mode
```bash
# Start FastAPI server
python -m uvicorn app.main:app --reload

# Start Streamlit frontend
streamlit run app/frontend/streamlit_app.py
```

## 📁 Project Structure

```
Hemist/
├── app/
│   ├── agents/           # AI Agent implementations
│   │   ├── coordinator/  # Workflow orchestration
│   │   ├── editor/       # Content editing & quality
│   │   ├── memory/       # Context management
│   │   ├── researcher/   # Web research & insights
│   │   └── writer/       # Content generation
│   ├── core/             # Core system components
│   │   ├── state_machine.py      # Workflow state management
│   │   ├── base_agent.py         # Agent base classes
│   │   ├── memory_manager.py     # Memory storage
│   │   ├── agent_communication.py # Inter-agent messaging
│   │   ├── workflow_orchestrator.py # Workflow coordination
│   │   └── workflow_persistence.py # State persistence
│   ├── database/         # Database models & connection
│   ├── api/              # FastAPI endpoints
│   └── frontend/         # Streamlit dashboard
├── run_ai_agents.py      # Command-line interface
├── requirements.txt       # Python dependencies
└── README_COMPLETE.md    # This file
```

## 🔑 Configuration

### Environment Variables
```bash
# Required for OpenAI features
export OPENAI_API_KEY="your_openai_api_key"

# Optional: Database configuration
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
export REDIS_URL="redis://localhost:6379"
```

### Configuration Files
- `config/settings.py` - System configuration
- `env.template` - Environment variables template

## 🚀 Production Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Run individual services
docker-compose up postgres redis
docker-compose up ai_agents
docker-compose up celery_worker
```

### Local Production
```bash
# Start all services
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
streamlit run app/frontend/streamlit_app.py --server.port 8501
celery -A app.core.celery_app worker --loglevel=info
```

## 📊 Monitoring and Logging

### System Monitoring
- **FastAPI**: `/health` endpoint for system status
- **Streamlit**: Real-time dashboard for workflow monitoring
- **Logs**: Structured logging with `structlog`
- **Metrics**: Performance monitoring and analytics

### Workflow Tracking
- **State Persistence**: Automatic workflow state saving
- **Progress Tracking**: Real-time workflow progress updates
- **Error Handling**: Comprehensive error logging and recovery
- **Performance Metrics**: Workflow execution time and quality scores

## 🛠️ Troubleshooting

### Common Issues

1. **OpenAI API Errors**: System works without API key using fallback methods
2. **Memory Issues**: Check available RAM and disk space
3. **Network Errors**: Verify internet connection for web research
4. **Import Errors**: Ensure virtual environment is activated

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python run_ai_agents.py --interactive
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to all functions
- Include error handling

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Getting Help
1. Check this README for usage examples
2. Review the test files for implementation details
3. Check the logs for error messages
4. Open an issue on GitHub

### Community
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and community support
- **Wiki**: Additional documentation and examples

---

## 🎉 Congratulations!

You now have a **production-ready AI Agents System** that can:

- 🔍 **Research** any topic automatically
- ✍️ **Write** high-quality content in multiple styles
- 🔍 **Edit** and improve content quality
- 🧠 **Remember** and learn from previous work
- 🎯 **Coordinate** complex multi-agent workflows
- 💾 **Persist** workflow states and results

**Next Steps:**
1. Test the system with your own topics
2. Customize the writing styles and quality parameters
3. Integrate with your existing content workflows
4. Extend the system with new agents and capabilities

**Happy Content Generation! 🚀** 