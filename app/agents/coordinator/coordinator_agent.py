"""
Coordinator Agent for AI Agents System
Orchestrates the entire content generation workflow
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
import uuid

from app.core import BaseAgent, AgentType, AgentCommunicationHub
from app.agents.researcher import ResearchAgent
from app.agents.writer import WriterAgent
from app.agents.editor import EditorAgent

logger = structlog.get_logger()

class CoordinatorAgent(BaseAgent):
    """Coordinator Agent for orchestrating content generation workflow"""
    
    def __init__(self, agent_id: str, name: str = "Coordinator Agent"):
        super().__init__(agent_id, AgentType.COORDINATOR, name)
        
        # Initialize communication hub
        self.communication_hub = AgentCommunicationHub()
        
        # Initialize sub-agents
        self.researcher = None
        self.writer = None
        self.editor = None
        
        # Workflow state
        self.current_workflow = None
        self.workflow_history = []
        self.agent_statuses = {}
        
        logger.info(f"Coordinator Agent {name} initialized")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete content generation workflow"""
        try:
            topic = context.get("topic", "Unknown topic")
            target_length = context.get("target_length", 1500)
            writing_style = context.get("writing_style", "professional")
            target_quality = context.get("target_quality", 0.9)
            research_depth = context.get("research_depth", "comprehensive")
            
            await self.start_task(f"Coordinating content generation for: {topic}")
            
            # Phase 1: Initialize and coordinate agents
            await self.update_progress(0.1, "Initializing and coordinating agents")
            await self._initialize_agents()
            
            # Phase 2: Research phase
            await self.update_progress(0.2, "Initiating research phase")
            research_result = await self._execute_research_phase(topic, research_depth)
            
            # Phase 3: Writing phase
            await self.update_progress(0.5, "Initiating writing phase")
            writing_result = await self._execute_writing_phase(topic, target_length, research_result, writing_style)
            
            # Phase 4: Editing phase
            await self.update_progress(0.8, "Initiating editing phase")
            editing_result = await self._execute_editing_phase(
                writing_result.get("content", ""), topic, research_result, target_quality
            )
            
            # Phase 5: Final coordination and quality assurance
            await self.update_progress(0.9, "Final coordination and quality assurance")
            final_result = await self._finalize_workflow(topic, research_result, writing_result, editing_result)
            
            # Store workflow results
            await self._store_workflow_results(topic, final_result)
            
            await self.update_progress(1.0, "Content generation workflow completed")
            await self.complete_task({
                "topic": topic,
                "workflow_duration": self._calculate_workflow_duration(),
                "final_quality": editing_result.get("quality_score", 0),
                "agents_used": len([self.researcher, self.writer, self.editor])
            })
            
            return final_result
            
        except Exception as e:
            logger.error(f"Workflow coordination failed: {e}")
            await self.handle_error(e, "workflow coordination")
            return {"status": "error", "error": str(e)}
    
    async def _initialize_agents(self):
        """Initialize and coordinate all sub-agents"""
        try:
            logger.info("Initializing and coordinating agents")
            
            # Create agent instances
            self.researcher = ResearchAgent("researcher_001", "Research Specialist")
            self.writer = WriterAgent("writer_001", "Content Writer")
            self.editor = EditorAgent("editor_001", "Quality Editor")
            
            # Register agents with communication hub
            await self.communication_hub.register_agent(self.researcher.agent_id, self.researcher.name)
            await self.communication_hub.register_agent(self.writer.agent_id, self.writer.name)
            await self.communication_hub.register_agent(self.editor.agent_id, self.editor.name)
            
            # Start communication hub
            await self.communication_hub.start()
            
            # Initialize agents
            await self.researcher.initialize()
            await self.writer.initialize()
            await self.editor.initialize()
            
            # Update agent statuses
            self.agent_statuses = {
                "researcher": "ready",
                "writer": "ready",
                "editor": "ready"
            }
            
            logger.info("All agents initialized and coordinated successfully")
            
        except Exception as e:
            logger.error(f"Agent initialization failed: {e}")
            raise
    
    async def _execute_research_phase(self, topic: str, research_depth: str) -> Dict[str, Any]:
        """Execute the research phase"""
        try:
            logger.info(f"Executing research phase for topic: {topic}")
            
            # Prepare research context
            research_context = {
                "topic": topic,
                "depth": research_depth,
                "max_sources": 10 if research_depth == "comprehensive" else 5,
                "include_statistics": True,
                "include_examples": True
            }
            
            # Execute research
            research_result = await self.researcher.execute(research_context)
            
            if research_result.get("status") == "success":
                logger.info("Research phase completed successfully")
                
                # Update agent status
                self.agent_statuses["researcher"] = "completed"
                
                # Store research insights
                await self.store_memory(
                    f"Research completed for {topic}: {len(research_result.get('insights', []))} insights",
                    "research_completion",
                    0.8,
                    {
                        "topic": topic,
                        "insights_count": len(research_result.get("insights", [])),
                        "sources_count": len(research_result.get("sources", [])),
                        "research_quality": research_result.get("research_quality", 0)
                    }
                )
                
                return research_result
            else:
                logger.error(f"Research phase failed: {research_result.get('error')}")
                raise Exception(f"Research phase failed: {research_result.get('error')}")
                
        except Exception as e:
            logger.error(f"Research phase execution failed: {e}")
            self.agent_statuses["researcher"] = "error"
            raise
    
    async def _execute_writing_phase(self, topic: str, target_length: int, 
                                   research_result: Dict[str, Any], writing_style: str) -> Dict[str, Any]:
        """Execute the writing phase"""
        try:
            logger.info(f"Executing writing phase for topic: {topic}")
            
            # Prepare writing context
            writing_context = {
                "topic": topic,
                "target_length": target_length,
                "research_data": research_result,
                "writing_style": writing_style,
                "include_citations": True,
                "target_audience": "general"
            }
            
            # Execute writing
            writing_result = await self.writer.execute(writing_context)
            
            if writing_result.get("status") == "success":
                logger.info("Writing phase completed successfully")
                
                # Update agent status
                self.agent_statuses["writer"] = "completed"
                
                # Store writing results
                await self.store_memory(
                    f"Writing completed for {topic}: {writing_result.get('word_count', 0)} words",
                    "writing_completion",
                    0.8,
                    {
                        "topic": topic,
                        "word_count": writing_result.get("word_count", 0),
                        "writing_style": writing_style,
                        "quality_score": writing_result.get("quality_score", 0)
                    }
                )
                
                return writing_result
            else:
                logger.error(f"Writing phase failed: {writing_result.get('error')}")
                raise Exception(f"Writing phase failed: {writing_result.get('error')}")
                
        except Exception as e:
            logger.error(f"Writing phase execution failed: {e}")
            self.agent_statuses["writer"] = "error"
            raise
    
    async def _execute_editing_phase(self, content: str, topic: str, 
                                   research_result: Dict[str, Any], target_quality: float) -> Dict[str, Any]:
        """Execute the editing phase"""
        try:
            logger.info(f"Executing editing phase for topic: {topic}")
            
            # Prepare editing context
            editing_context = {
                "content": content,
                "topic": topic,
                "research_data": research_result,
                "target_quality": target_quality,
                "editing_style": "comprehensive",
                "include_fact_checking": True,
                "include_quality_analysis": True
            }
            
            # Execute editing
            editing_result = await self.editor.execute(editing_context)
            
            if editing_result.get("status") == "success":
                logger.info("Editing phase completed successfully")
                
                # Update agent status
                self.agent_statuses["editor"] = "completed"
                
                # Store editing results
                await self.store_memory(
                    f"Editing completed for {topic}: Quality improved to {editing_result.get('quality_score', 0):.2f}",
                    "editing_completion",
                    0.9,
                    {
                        "topic": topic,
                        "final_quality": editing_result.get("quality_score", 0),
                        "improvements_made": editing_result.get("improvements_made", 0),
                        "editing_style": editing_result.get("editing_style", "")
                    }
                )
                
                return editing_result
            else:
                logger.error(f"Editing phase failed: {editing_result.get('error')}")
                raise Exception(f"Editing phase failed: {editing_result.get('error')}")
                
        except Exception as e:
            logger.error(f"Editing phase execution failed: {e}")
            self.agent_statuses["editor"] = "error"
            raise
    
    async def _finalize_workflow(self, topic: str, research_result: Dict[str, Any], 
                               writing_result: Dict[str, Any], editing_result: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize the complete workflow"""
        try:
            logger.info(f"Finalizing workflow for topic: {topic}")
            
            # Compile final result
            final_result = {
                "status": "success",
                "topic": topic,
                "workflow_summary": {
                    "research_phase": {
                        "status": "completed",
                        "insights_count": len(research_result.get("insights", [])),
                        "sources_count": len(research_result.get("sources", [])),
                        "research_quality": research_result.get("research_quality", 0)
                    },
                    "writing_phase": {
                        "status": "completed",
                        "word_count": writing_result.get("word_count", 0),
                        "writing_style": writing_result.get("writing_style", ""),
                        "writing_quality": writing_result.get("quality_score", 0)
                    },
                    "editing_phase": {
                        "status": "completed",
                        "final_quality": editing_result.get("quality_score", 0),
                        "improvements_made": editing_result.get("improvements_made", 0),
                        "editing_style": editing_result.get("editing_style", "")
                    }
                },
                "final_content": editing_result.get("edited_content", ""),
                "final_quality": editing_result.get("quality_score", 0),
                "workflow_metadata": {
                    "coordinator_id": self.agent_id,
                    "workflow_id": str(uuid.uuid4()),
                    "started_at": self.state.last_activity.isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "total_duration": self._calculate_workflow_duration()
                }
            }
            
            # Update workflow history
            self.workflow_history.append({
                "workflow_id": final_result["workflow_metadata"]["workflow_id"],
                "topic": topic,
                "status": "completed",
                "final_quality": final_result["final_quality"],
                "completed_at": final_result["workflow_metadata"]["completed_at"]
            })
            
            logger.info(f"Workflow finalized successfully for topic: {topic}")
            return final_result
            
        except Exception as e:
            logger.error(f"Workflow finalization failed: {e}")
            raise
    
    def _calculate_workflow_duration(self) -> str:
        """Calculate the duration of the current workflow"""
        try:
            if not self.state.last_activity:
                return "Unknown"
            
            duration = datetime.now() - self.state.last_activity
            total_seconds = int(duration.total_seconds())
            
            if total_seconds < 60:
                return f"{total_seconds} seconds"
            elif total_seconds < 3600:
                minutes = total_seconds // 60
                return f"{minutes} minutes"
            else:
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                return f"{hours} hours {minutes} minutes"
                
        except Exception as e:
            logger.error(f"Duration calculation failed: {e}")
            return "Unknown"
    
    async def _store_workflow_results(self, topic: str, final_result: Dict[str, Any]):
        """Store comprehensive workflow results"""
        try:
            # Store workflow overview
            await self.store_memory(
                f"Complete workflow completed for {topic}. Final quality: {final_result.get('final_quality', 0):.2f}",
                "workflow_completion",
                0.9,
                {
                    "topic": topic,
                    "final_quality": final_result.get("final_quality", 0),
                    "workflow_id": final_result.get("workflow_metadata", {}).get("workflow_id", ""),
                    "total_duration": final_result.get("workflow_metadata", {}).get("total_duration", "")
                }
            )
            
            logger.info(f"Stored workflow results for topic: {topic}")
            
        except Exception as e:
            logger.error(f"Failed to store workflow results: {e}")
    
    async def get_workflow_status(self, workflow_id: str = None) -> Dict[str, Any]:
        """Get current workflow status"""
        try:
            if workflow_id:
                # Return specific workflow status
                for workflow in self.workflow_history:
                    if workflow.get("workflow_id") == workflow_id:
                        return workflow
                return {"error": f"Workflow {workflow_id} not found"}
            
            # Return current workflow status
            return {
                "current_workflow": self.current_workflow,
                "agent_statuses": self.agent_statuses,
                "workflow_history": self.workflow_history[-5:],  # Last 5 workflows
                "coordinator_status": self.status.value,
                "last_activity": self.state.last_activity.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow status: {e}")
            return {"error": str(e)}
    
    async def pause_workflow(self) -> bool:
        """Pause the current workflow"""
        try:
            logger.info("Pausing current workflow")
            
            # Pause all agents
            if self.researcher:
                self.researcher.status = "paused"
            if self.writer:
                self.writer.status = "paused"
            if self.editor:
                self.editor.status = "paused"
            
            self.status = "paused"
            logger.info("Workflow paused successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to pause workflow: {e}")
            return False
    
    async def resume_workflow(self) -> bool:
        """Resume the paused workflow"""
        try:
            logger.info("Resuming paused workflow")
            
            # Resume all agents
            if self.researcher:
                self.researcher.status = "busy"
            if self.writer:
                self.writer.status = "busy"
            if self.editor:
                self.editor.status = "busy"
            
            self.status = "busy"
            logger.info("Workflow resumed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to resume workflow: {e}")
            return False
    
    async def cancel_workflow(self) -> bool:
        """Cancel the current workflow"""
        try:
            logger.info("Cancelling current workflow")
            
            # Cancel all agents
            if self.researcher:
                self.researcher.status = "idle"
            if self.writer:
                self.writer.status = "idle"
            if self.editor:
                self.editor.status = "idle"
            
            self.status = "idle"
            self.current_workflow = None
            logger.info("Workflow cancelled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel workflow: {e}")
            return False
    
    async def get_agent_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all agents"""
        try:
            metrics = {}
            
            # Research agent metrics
            if self.researcher:
                research_memories = await self.researcher.get_research_history()
                metrics["researcher"] = {
                    "status": self.researcher.status.value,
                    "research_count": len(research_memories),
                    "last_research": research_memories[-1] if research_memories else None
                }
            
            # Writer agent metrics
            if self.writer:
                writing_memories = await self.writer.get_writing_history()
                metrics["writer"] = {
                    "status": self.writer.status.value,
                    "writing_count": len(writing_memories),
                    "last_writing": writing_memories[-1] if writing_memories else None
                }
            
            # Editor agent metrics
            if self.editor:
                editing_memories = await self.editor.get_editing_history()
                metrics["editor"] = {
                    "status": self.editor.status.value,
                    "editing_count": len(editing_memories),
                    "last_editing": editing_memories[-1] if editing_memories else None
                }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get agent performance metrics: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Clean up resources and stop agents"""
        try:
            logger.info("Cleaning up coordinator agent")
            
            # Stop communication hub
            if self.communication_hub:
                await self.communication_hub.stop()
            
            # Clean up agents
            if self.researcher:
                await self.researcher.reset()
            if self.writer:
                await self.writer.reset()
            if self.editor:
                await self.editor.reset()
            
            logger.info("Coordinator agent cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}") 