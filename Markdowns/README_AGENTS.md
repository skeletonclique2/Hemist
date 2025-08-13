# 🤖 AI Agents System

Production-ready multi-agent AI system for content generation built with LangGraph, FastAPI, and PostgreSQL.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Coordinator    │◄──►│   Research       │◄──►│   Writer        │
│  Agent          │    │   Agent          │    │   Agent         │
└─────────┬───────┘    └──────────────────┘    └─────────────────┘
          │                                              ▲
          ▼                                              │
┌─────────────────┐    ┌──────────────────┐             │
│  Editor         │◄──►│   Memory         │─────────────┘
│  Agent          │    │   Store          │
└─────────────────┘    └──────────────────┘
```

## 🚀 Quick Start (5 minutes)

### 1. Prerequisites
- Docker and Docker Compose
- OpenAI API key
- Python 3.11+

### 2. Setup Environment
```bash
# Copy environment template
cp env.template .env

# Edit .env with your API keys
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Start the System
```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 4. Access the System
- **API Documentation**: http://localhost:8000/docs
- **Frontend Dashboard**: http://localhost:8501
- **Health Check**: http://localhost:8000/health

## 🏛️ Tech Stack

### Core Framework
- **LangGraph 0.0.38** - Agent orchestration and state machines
- **LangChain 0.1.17** - Agent framework and tools
- **FastAPI 0.104.1** - High-performance async API
- **Streamlit 1.28.1** - Interactive frontend dashboard

### Database & Storage
- **PostgreSQL 15** - Primary database with ACID compliance
- **pgvector** - Vector similarity search for embeddings
- **Redis 7** - Caching and message broker

### Production Features
- **Celery 5.3.4** - Distributed task processing
- **Structlog** - Structured logging
- **Prometheus** - Metrics collection
- **LangSmith** - Agent monitoring and tracing

## 📁 Project Structure

```
ai_agents/
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # Application container
├── requirements.txt            # Python dependencies
├── init.sql                   # Database initialization
├── app/                       # Main application
│   ├── main.py               # FastAPI entry point
│   ├── database/             # Database models and connection
│   ├── api/                  # API routes and endpoints
│   ├── frontend/             # Streamlit dashboard
│   ├── agents/               # AI agent implementations
│   ├── core/                 # Core system components
│   └── utils/                # Utility functions
└── README_AGENTS.md          # This file
```

## 🔧 Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up local PostgreSQL with pgvector
# (Use Docker for consistency)

# Run FastAPI server
uvicorn app.main:app --reload

# Run Streamlit frontend
streamlit run app/frontend/streamlit_app.py
```

### Docker Development
```bash
# Start services
docker-compose up

# View logs
docker-compose logs -f ai_agents

# Execute commands in container
docker-compose exec ai_agents bash

# Rebuild after changes
docker-compose up --build
```

## 🎯 Agent Types

### 1. Coordinator Agent
- Orchestrates workflow execution
- Manages agent communication
- Handles error recovery and retries

### 2. Research Agent
- Web search and content retrieval
- Knowledge extraction and summarization
- Source validation and credibility assessment

### 3. Writer Agent
- Content generation using GPT-4
- Iterative improvement based on feedback
- Style and tone adaptation

### 4. Editor Agent
- Quality control and fact-checking
- Grammar and style review
- Content optimization and SEO

### 5. Memory Agent
- Vector storage and retrieval
- Context management
- Learning from past interactions

## 📊 API Endpoints

### Core Endpoints
- `GET /` - System information
- `GET /health` - Health check
- `GET /api/v1/agents` - List all agents
- `GET /api/v1/workflows` - List workflows
- `POST /api/v1/workflows` - Create workflow

### Agent Endpoints
- `GET /api/v1/agents/{name}/status` - Agent status
- `POST /api/v1/agents/{name}/execute` - Execute agent task

## 🔍 Monitoring & Observability

### LangSmith Integration
- Agent decision tracing
- Performance metrics
- Error tracking and debugging

### Metrics Collection
- Prometheus metrics
- Custom business metrics
- Performance indicators

### Logging
- Structured JSON logging
- Log aggregation
- Error correlation

## 🚀 Production Deployment

### Environment Variables
```bash
ENVIRONMENT=production
LOG_LEVEL=WARNING
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port
```

### Scaling
- Horizontal scaling with multiple API instances
- Database connection pooling
- Redis cluster for high availability

### Security
- API key authentication
- Rate limiting
- Input validation and sanitization

## 🧪 Testing

### Unit Tests
```bash
pytest app/tests/unit/
```

### Integration Tests
```bash
pytest app/tests/integration/
```

### End-to-End Tests
```bash
pytest app/tests/e2e/
```

## 📈 Performance

### Benchmarks
- **API Response Time**: < 100ms for simple requests
- **Agent Execution**: < 30s for content generation
- **Database Queries**: < 50ms for vector similarity search
- **Concurrent Users**: 100+ simultaneous workflows

### Optimization
- Vector indexing for fast similarity search
- Redis caching for frequently accessed data
- Async processing for I/O operations
- Connection pooling for database efficiency

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: GitHub Issues
- **Documentation**: API docs at `/docs`
- **Community**: Join our Discord server

---

**Built with ❤️ using modern AI technologies** 