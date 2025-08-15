"""
Workflow Orchestrator for AI Agents System
Coordinates agent execution and manages workflow lifecycle
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid
import structlog
from enum import Enum

import langsmith
from prometheus_client import Counter, Histogram

from .state_machine import WorkflowStateMachine, WorkflowContext, WorkflowState
from .base_agent import BaseAgent, AgentStatus, AgentType
from .agent_communication import AgentCommunicationHub, AgentMessage, MessageType, MessagePriority

logger = structlog.get_logger()

# Prometheus metrics for workflow orchestration
WORKFLOW_STARTS = Counter("workflow_starts_total", "Total workflow executions started")
WORKFLOW_COMPLETIONS = Counter("workflow_completions_total", "Total workflow executions completed")
WORKFLOW_ERRORS = Counter("workflow_errors_total", "Total workflow execution errors")
WORKFLOW_DURATION = Histogram("workflow_duration_seconds", "Workflow execution duration in seconds")

class OrchestratorStatus(str, Enum):
    """Orchestrator status enumeration"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"

@dataclass
class WorkflowExecution:
    """Represents a workflow execution instance"""
    execution_id: str
    workflow_id: str
    status: str = "pending"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_agent: Optional[str] = None
    progress: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class WorkflowOrchestrator:
    """Orchestrates workflow execution and agent coordination"""
    
    def __init__(self):
        self.state_machine = WorkflowStateMachine()
        self.communication_hub = AgentCommunicationHub()
        self.agents: Dict[str, BaseAgent] = {}
        self.workflows: Dict[str, WorkflowExecution] = {}
        self.status = OrchestratorStatus.IDLE
        self.max_retries = 3
        self.retry_delay = 5.0  # seconds
        
        logger.info("Workflow Orchestrator initialized")
    
    async def start(self):
        """Start the orchestrator"""
        try:
            logger.info("Starting Workflow Orchestrator")
            self.status = OrchestratorStatus.IDLE
            
            # Start communication hub
            await self.communication_hub.start()
            
            logger.info("Workflow Orchestrator started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start orchestrator: {e}")
            self.status = OrchestratorStatus.ERROR
            raise
    
    async def stop(self):
        """Stop the orchestrator"""
        try:
            logger.info("Stopping Workflow Orchestrator")
            self.status = OrchestratorStatus.SHUTDOWN
            
            # Stop communication hub
            await self.communication_hub.stop()
            
            # Stop all running workflows
            await self._stop_all_workflows()
            
            logger.info("Workflow Orchestrator stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop orchestrator: {e}")
    
    async def register_agent(self, agent: BaseAgent) -> bool:
        """Register an agent with the orchestrator"""
        try:
            agent_id = agent.agent_id
            
            # Register with communication hub
            success = await self.communication_hub.register_agent(
                agent_id, 
                agent.name,
                self._create_agent_message_handler(agent)
            )
            
            if success:
                self.agents[agent_id] = agent
                logger.info(f"Agent {agent.name} registered with orchestrator")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent.name}: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the orchestrator"""
        try:
            if agent_id not in self.agents:
                logger.warning(f"Agent {agent_id} not registered")
                return False
            
            # Unregister from communication hub
            await self.communication_hub.unregister_agent(agent_id)
            
            # Remove from agents dict
            del self.agents[agent_id]
            
            logger.info(f"Agent {agent_id} unregistered from orchestrator")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False
    
    async def execute_workflow(self, topic: str, target_length: int = 1500, 
                             quality_threshold: float = 0.8) -> str:
        """Execute a new workflow with monitoring and tracing"""
        try:
            # Create workflow execution
            execution_id = f"exec_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            workflow_execution = WorkflowExecution(
                execution_id=execution_id,
                workflow_id=f"workflow_{uuid.uuid4().hex[:8]}",
                start_time=datetime.utcnow()
            )
            
            self.workflows[execution_id] = workflow_execution

            # Prometheus: increment workflow starts
            WORKFLOW_STARTS.inc()

            # Start workflow execution in background with tracing and duration histogram
            asyncio.create_task(self._execute_workflow_background_traced(
                execution_id, topic, target_length, quality_threshold
            ))
            
            logger.info(f"Started workflow execution: {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Failed to start workflow execution: {e}")
            raise
    
    async def _execute_workflow_background_traced(self, execution_id: str, topic: str, 
                                         target_length: int, quality_threshold: float):
        """Execute workflow in background with tracing, metrics, and retry logic"""
        with langsmith.trace("workflow_execution", execution_id=execution_id, topic=topic):
            start_time = datetime.utcnow()
            max_retries = 3
            retry_delay = 5  # seconds
            retries = 0
            while retries <= max_retries:
                try:
                    workflow_execution = self.workflows[execution_id]
                    workflow_execution.status = "running"
                    
                    # Execute workflow using state machine
                    result = await self.state_machine.execute_workflow(
                        topic, target_length, quality_threshold
                    )
                    
                    # Update execution status
                    workflow_execution.status = "completed"
                    workflow_execution.end_time = datetime.utcnow()
                    workflow_execution.progress = 1.0

                    # Prometheus: record duration and completion
                    duration = (workflow_execution.end_time - start_time).total_seconds()
                    WORKFLOW_DURATION.observe(duration)
                    WORKFLOW_COMPLETIONS.inc()
                    
                    # Store result in memory
                    await self._store_workflow_result(execution_id, result)
                    
                    logger.info(f"Workflow execution {execution_id} completed successfully")
                    return
                    
                except Exception as e:
                    logger.error(f"Workflow execution {execution_id} failed (attempt {retries+1}/{max_retries+1}): {e}")
                    workflow_execution.status = "error"
                    workflow_execution.error_message = str(e)
                    workflow_execution.end_time = datetime.utcnow()
                    WORKFLOW_ERRORS.inc()
                    retries += 1
                    if retries <= max_retries:
                        logger.info(f"Retrying workflow execution {execution_id} in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                    else:
                        logger.error(f"Workflow execution {execution_id} failed after {max_retries} retries.")
                        raise
    
    async def _store_workflow_result(self, execution_id: str, result: WorkflowContext):
        """Store workflow result in memory"""
        try:
            # This would typically store in the database
            # For now, just log the result
            logger.info(f"Workflow {execution_id} result: {result.current_state}")
            
        except Exception as e:
            logger.error(f"Failed to store workflow result: {e}")
    
    async def pause_workflow(self, execution_id: str) -> bool:
        """Pause a running workflow"""
        try:
            if execution_id not in self.workflows:
                logger.warning(f"Workflow {execution_id} not found")
                return False
            
            workflow = self.workflows[execution_id]
            if workflow.status == "running":
                workflow.status = "paused"
                logger.info(f"Workflow {execution_id} paused")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to pause workflow {execution_id}: {e}")
            return False
    
    async def resume_workflow(self, execution_id: str) -> bool:
        """Resume a paused workflow"""
        try:
            if execution_id not in self.workflows:
                logger.warning(f"Workflow {execution_id} not found")
                return False
            
            workflow = self.workflows[execution_id]
            if workflow.status == "paused":
                workflow.status = "running"
                logger.info(f"Workflow {execution_id} resumed")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to resume workflow {execution_id}: {e}")
            return False
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a workflow"""
        try:
            if execution_id not in self.workflows:
                logger.warning(f"Workflow {execution_id} not found")
                return False
            
            workflow = self.workflows[execution_id]
            workflow.status = "cancelled"
            workflow.end_time = datetime.utcnow()
            
            logger.info(f"Workflow {execution_id} cancelled")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel workflow {execution_id}: {e}")
            return False
    
    async def get_workflow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a workflow execution"""
        try:
            if execution_id not in self.workflows:
                return None
            
            workflow = self.workflows[execution_id]
            
            return {
                "execution_id": workflow.execution_id,
                "workflow_id": workflow.workflow_id,
                "status": workflow.status,
                "start_time": workflow.start_time.isoformat() if workflow.start_time else None,
                "end_time": workflow.end_time.isoformat() if workflow.end_time else None,
                "current_agent": workflow.current_agent,
                "progress": workflow.progress,
                "error_message": workflow.error_message,
                "metadata": workflow.metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow status for {execution_id}: {e}")
            return None
    
    async def get_all_workflows(self) -> List[Dict[str, Any]]:
        """Get status of all workflows"""
        try:
            workflows = []
            for execution_id in self.workflows:
                status = await self.get_workflow_status(execution_id)
                if status:
                    workflows.append(status)
            
            return workflows
            
        except Exception as e:
            logger.error(f"Failed to get all workflow statuses: {e}")
            return []
    
    def _create_agent_message_handler(self, agent: BaseAgent) -> Callable:
        """Create a message handler for an agent"""
        async def message_handler(message: AgentMessage):
            try:
                logger.debug(f"Agent {agent.name} received message: {message.message_type}")
                
                # Handle different message types
                if message.message_type == MessageType.TASK_REQUEST:
                    await self._handle_task_request(agent, message)
                elif message.message_type == MessageType.STATUS_UPDATE:
                    await self._handle_status_update(agent, message)
                elif message.message_type == MessageType.ERROR_NOTIFICATION:
                    await self._handle_error_notification(agent, message)
                
                # Acknowledge message
                await self.communication_hub.acknowledge_message(message.id, agent.agent_id)
                
            except Exception as e:
                logger.error(f"Message handler failed for agent {agent.name}: {e}")
        
        return message_handler
    
    async def _handle_task_request(self, agent: BaseAgent, message: AgentMessage):
        """Handle task request from an agent"""
        try:
            # Extract task details from message
            task_data = message.content.get("task", {})
            task_type = task_data.get("type")
            task_params = task_data.get("parameters", {})
            
            logger.info(f"Agent {agent.name} requesting task: {task_type}")
            
            # Execute task based on type
            if task_type == "research":
                await self._execute_research_task(agent, task_params)
            elif task_type == "write":
                await self._execute_write_task(agent, task_params)
            elif task_type == "edit":
                await self._execute_edit_task(agent, task_params)
            else:
                logger.warning(f"Unknown task type: {task_type}")
                
        except Exception as e:
            logger.error(f"Failed to handle task request: {e}")
    
    async def _handle_status_update(self, agent: BaseAgent, message: AgentMessage):
        """Handle status update from an agent"""
        try:
            status_data = message.content.get("status", {})
            logger.debug(f"Agent {agent.name} status update: {status_data}")
            
            # Update agent status in orchestrator
            # This could trigger workflow state transitions
            
        except Exception as e:
            logger.error(f"Failed to handle status update: {e}")
    
    async def _handle_error_notification(self, agent: BaseAgent, message: AgentMessage):
        """Handle error notification from an agent"""
        try:
            error_data = message.content.get("error", {})
            logger.error(f"Agent {agent.name} error: {error_data}")
            
            # Handle agent error - could trigger retry or workflow failure
            
        except Exception as e:
            logger.error(f"Failed to handle error notification: {e}")
    
    async def _execute_research_task(self, agent: BaseAgent, params: Dict[str, Any]):
        """Execute research task"""
        # Placeholder for research task execution
        logger.info(f"Executing research task for agent {agent.name}")
    
    async def _execute_write_task(self, agent: BaseAgent, params: Dict[str, Any]):
        """Execute writing task"""
        # Placeholder for writing task execution
        logger.info(f"Executing writing task for agent {agent.name}")
    
    async def _execute_edit_task(self, agent: BaseAgent, params: Dict[str, Any]):
        """Execute editing task"""
        # Placeholder for editing task execution
        logger.info(f"Executing editing task for agent {agent.name}")
    
    async def _stop_all_workflows(self):
        """Stop all running workflows"""
        try:
            for execution_id in self.workflows:
                if self.workflows[execution_id].status == "running":
                    await self.cancel_workflow(execution_id)
                    
        except Exception as e:
            logger.error(f"Failed to stop all workflows: {e}")
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            "status": self.status.value,
            "registered_agents": len(self.agents),
            "active_workflows": len([w for w in self.workflows.values() if w.status == "running"]),
            "total_workflows": len(self.workflows),
            "communication_hub_status": self.communication_hub.get_hub_status()
        }
    
    def get_agent_statuses(self) -> List[Dict[str, Any]]:
        """Get status of all registered agents"""
        try:
            agent_statuses = []
            for agent in self.agents.values():
                status = agent.get_status()
                status["communication_status"] = self.communication_hub.get_agent_status(agent.agent_id)
                agent_statuses.append(status)
            
            return agent_statuses
            
        except Exception as e:
            logger.error(f"Failed to get agent statuses: {e}")
            return []
