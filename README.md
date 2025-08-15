# AI Agents System

This is a production-ready multi-agent AI system for content generation.

## Features

- **Multi-Agent Architecture**: The system is designed with a multi-agent architecture, allowing for specialized agents to handle different tasks such as research, writing, and editing.
- **Workflow Orchestration**: The system uses a workflow orchestrator to manage the execution of tasks across different agents.
- **API First**: The system is built with an API-first approach, allowing for easy integration with other systems.
- **Authentication and Authorization**: The system provides authentication and authorization features to secure the API endpoints.

## Authentication and Authorization

The system uses JWT for authentication and role-based access control (RBAC) for authorization.

### Roles

- `admin`: Can create, view, and manage agents and workflows.
- `user`: Can view agents and workflows.

### Endpoints

- `POST /auth/login`: Authenticate a user and get a JWT token.
- `GET /api/v1/agents`: Get all agents (requires `admin` or `user` role).
- `GET /api/v1/agents/{agent_name}/status`: Get the status of an agent (requires `admin` or `user` role).
- `GET /api/v1/workflows`: Get all workflows (requires `admin` or `user` role).
- `POST /api/v1/workflows`: Create a new workflow (requires `admin` role).

## Getting Started

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/ai-agents-system.git
    ```
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set up the environment**:
    - Create a `.env` file and add the following variables:
      ```
      SECRET_KEY=your-secret-key
      ```
4.  **Run the application**:
    ```bash
    uvicorn app.main:app --reload
    ```

## Usage

1.  **Get a JWT token**:
    - Send a `POST` request to `/auth/login` with the following body:
      ```json
      {
        "username": "admin",
        "password": "adminpassword"
      }
      ```
2.  **Access protected endpoints**:
    - Include the JWT token in the `Authorization` header:
      ```
      Authorization: Bearer <your-jwt-token>

run this with:

backend: uvicorn app.main:app --reload
frontend: streamlit run app/frontend/streamlit_app.py
