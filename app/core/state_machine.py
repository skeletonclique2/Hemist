"""
LangGraph State Machine for AI Agents System
Manages workflow states and transitions between agents
"""

from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import structlog
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

logger = structlog.get_logger()

class WorkflowState(str, Enum):
    """Workflow states for the AI agents system"""
    PENDING = "pending"
    RESEARCHING = "researching"
    WRITING = "writing"
    EDITING = "editing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class WorkflowContext:
    """Context data passed between workflow states"""
    workflow_id: str
    topic: str
    target_length: int = 1500
    quality_threshold: float = 0.8
    
    # Research phase data
    research_sources: List[Dict[str, Any]] = field(default_factory=list)
    key_insights: List[str] = field(default_factory=list)
    
    # Writing phase data
    draft_content: str = ""
    word_count: int = 0
    
    # Editing phase data
    final_content: str = ""
    quality_score: float = 0.0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    current_state: WorkflowState = WorkflowState.PENDING
    error_message: Optional[str] = None
    
    def update_state(self, new_state: WorkflowState, **kwargs):
        """Update workflow state and timestamp"""
        self.current_state = new_state
        self.updated_at = datetime.utcnow()
        
        # Update any additional fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        logger.info(f"Workflow {self.workflow_id} transitioned to {new_state}")

class WorkflowStateMachine:
    """LangGraph state machine for AI agent workflows"""
    
    def __init__(self):
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state machine"""
        # Create the graph
        workflow = StateGraph(WorkflowContext)
        
        # Add nodes for each workflow phase
        workflow.add_node("research", self._research_phase)
        workflow.add_node("write", self._write_phase)
        workflow.add_node("edit", self._edit_phase)
        workflow.add_node("complete", self._complete_phase)
        workflow.add_node("error_handler", self._error_handler)
        
        # Define the workflow flow
        workflow.set_entry_point("research")
        
        # Research -> Write
        workflow.add_edge("research", "write")
        
        # Write -> Edit
        workflow.add_edge("write", "edit")
        
        # Edit -> Complete
        workflow.add_edge("edit", "complete")
        
        # Complete -> END
        workflow.add_edge("complete", END)
        
        # Error handling - any state can transition to error
        workflow.add_edge("error_handler", END)
        
        # Add conditional edges for error handling
        workflow.add_conditional_edges(
            "research",
            self._should_continue,
            {
                "continue": "write",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "write",
            self._should_continue,
            {
                "continue": "edit",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "edit",
            self._should_continue,
            {
                "continue": "complete",
                "error": "error_handler"
            }
        )
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    def _should_continue(self, state: WorkflowContext) -> str:
        """Determine if workflow should continue or handle error"""
        if state.error_message:
            return "error"
        return "continue"
    
    async def _research_phase(self, state: WorkflowContext) -> WorkflowContext:
        """Research phase - gather information and insights"""
        try:
            logger.info(f"Starting research phase for workflow {state.workflow_id}")
            state.update_state(WorkflowState.RESEARCHING)
            
            # Simulate research process (will be replaced with actual research agent)
            state.research_sources = [
                {"title": "Sample Research Source", "url": "https://example.com", "content": "Sample content"}
            ]
            state.key_insights = ["Key insight 1", "Key insight 2"]
            
            logger.info(f"Research phase completed for workflow {state.workflow_id}")
            return state
            
        except Exception as e:
            logger.error(f"Research phase failed: {e}")
            state.error_message = f"Research failed: {str(e)}"
            return state
    
    async def _write_phase(self, state: WorkflowContext) -> WorkflowContext:
        """Writing phase - generate initial content"""
        try:
            logger.info(f"Starting writing phase for workflow {state.workflow_id}")
            state.update_state(WorkflowState.WRITING)
            
            # Simulate writing process (will be replaced with actual writer agent)
            state.draft_content = f"Sample content about {state.topic}. This is a draft with approximately {state.target_length} words."
            state.word_count = len(state.draft_content.split())
            
            logger.info(f"Writing phase completed for workflow {state.workflow_id}")
            return state
            
        except Exception as e:
            logger.error(f"Writing phase failed: {e}")
            state.error_message = f"Writing failed: {str(e)}"
            return state
    
    async def _edit_phase(self, state: WorkflowContext) -> WorkflowContext:
        """Editing phase - refine and optimize content"""
        try:
            logger.info(f"Starting editing phase for workflow {state.workflow_id}")
            state.update_state(WorkflowState.EDITING)
            
            # Simulate editing process (will be replaced with actual editor agent)
            state.final_content = state.draft_content + " [Edited and optimized]"
            state.quality_score = 0.85  # Simulated quality score
            
            logger.info(f"Editing phase completed for workflow {state.workflow_id}")
            return state
            
        except Exception as e:
            logger.error(f"Editing phase failed: {e}")
            state.error_message = f"Editing failed: {str(e)}"
            return state
    
    async def _complete_phase(self, state: WorkflowContext) -> WorkflowContext:
        """Completion phase - finalize workflow"""
        try:
            logger.info(f"Completing workflow {state.workflow_id}")
            state.update_state(WorkflowState.COMPLETED)
            
            # Finalize workflow data
            state.updated_at = datetime.utcnow()
            
            logger.info(f"Workflow {state.workflow_id} completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Completion phase failed: {e}")
            state.error_message = f"Completion failed: {str(e)}"
            return state
    
    async def _error_handler(self, state: WorkflowContext) -> WorkflowContext:
        """Handle errors in workflow execution"""
        logger.error(f"Error in workflow {state.workflow_id}: {state.error_message}")
        state.update_state(WorkflowState.ERROR)
        return state
    
    async def execute_workflow(self, topic: str, target_length: int = 1500, quality_threshold: float = 0.8) -> WorkflowContext:
        """Execute a complete workflow"""
        workflow_id = f"workflow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize workflow context
        context = WorkflowContext(
            workflow_id=workflow_id,
            topic=topic,
            target_length=target_length,
            quality_threshold=quality_threshold
        )
        
        logger.info(f"Starting workflow {workflow_id} for topic: {topic}")
        
        try:
            # Execute the workflow
            result = await self.graph.ainvoke(context)
            logger.info(f"Workflow {workflow_id} executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} execution failed: {e}")
            context.error_message = f"Workflow execution failed: {str(e)}"
            context.update_state(WorkflowState.ERROR)
            return context
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowContext]:
        """Get the current status of a workflow"""
        try:
            # This would typically query the memory/checkpoint system
            # For now, return None as we haven't implemented persistence yet
            return None
        except Exception as e:
            logger.error(f"Failed to get workflow status for {workflow_id}: {e}")
            return None 