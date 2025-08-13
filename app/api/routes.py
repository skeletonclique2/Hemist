from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
import structlog

from app.database.connection import get_db
from app.database.models import Agent, AgentState, Workflow

logger = structlog.get_logger()
router = APIRouter()

@router.get("/health")
async def api_health_check():
    """API health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-agents-api",
        "version": "1.0.0"
    }

@router.get("/agents", response_model=List[Dict[str, Any]])
async def get_agents(db: AsyncSession = Depends(get_db)):
    """Get all agents in the system"""
    try:
        result = await db.execute(select(Agent))
        agents = result.scalars().all()
        
        return [
            {
                "id": str(agent.id),
                "name": agent.name,
                "type": agent.agent_type,
                "status": agent.status,
                "created_at": agent.created_at.isoformat() if agent.created_at else None
            }
            for agent in agents
        ]
    except Exception as e:
        logger.error("Failed to fetch agents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch agents"
        )

@router.get("/agents/{agent_name}/status")
async def get_agent_status(agent_name: str, db: AsyncSession = Depends(get_db)):
    """Get status of a specific agent"""
    try:
        result = await db.execute(
            select(Agent).where(Agent.name == agent_name)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_name}' not found"
            )
        
        return {
            "name": agent.name,
            "type": agent.agent_type,
            "status": agent.status,
            "last_updated": agent.updated_at.isoformat() if agent.updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch agent status for {agent_name}", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch agent status"
        )

@router.get("/workflows", response_model=List[Dict[str, Any]])
async def get_workflows(db: AsyncSession = Depends(get_db)):
    """Get all workflows in the system"""
    try:
        result = await db.execute(select(Workflow))
        workflows = result.scalars().all()
        
        return [
            {
                "id": str(workflow.id),
                "name": workflow.name,
                "status": workflow.status,
                "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
                "updated_at": workflow.updated_at.isoformat() if workflow.updated_at else None
            }
            for workflow in workflows
        ]
    except Exception as e:
        logger.error("Failed to fetch workflows", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch workflows"
        )

@router.post("/workflows")
async def create_workflow(
    workflow_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """Create a new workflow"""
    try:
        workflow = Workflow(
            name=workflow_data.get("name", "Unnamed Workflow"),
            workflow_data=workflow_data,
            status="pending"
        )
        
        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)
        
        logger.info(f"Created workflow: {workflow.name}")
        
        return {
            "id": str(workflow.id),
            "name": workflow.name,
            "status": workflow.status,
            "created_at": workflow.created_at.isoformat() if workflow.created_at else None
        }
    except Exception as e:
        logger.error("Failed to create workflow", error=str(e))
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create workflow"
        )

@router.get("/system/status")
async def get_system_status():
    """Get overall system status"""
    return {
        "status": "operational",
        "components": {
            "database": "connected",
            "redis": "connected",
            "agents": "active",
            "workflows": "running"
        },
        "version": "1.0.0"
    } 