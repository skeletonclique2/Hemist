"""
Workflow Persistence System for AI Agents System
Handles saving and loading workflow states, progress, and results
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
import uuid
from pathlib import Path

logger = structlog.get_logger()

class WorkflowPersistence:
    """Manages workflow state persistence and recovery"""
    
    def __init__(self, storage_path: str = "workflow_states"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Ensure subdirectories exist
        (self.storage_path / "active").mkdir(exist_ok=True)
        (self.storage_path / "completed").mkdir(exist_ok=True)
        (self.storage_path / "failed").mkdir(exist_ok=True)
        (self.storage_path / "archived").mkdir(exist_ok=True)
        
        logger.info(f"Workflow persistence initialized at {self.storage_path}")
    
    async def save_workflow_state(self, workflow_id: str, state: Dict[str, Any], 
                                status: str = "active") -> bool:
        """Save workflow state to disk"""
        try:
            # Add metadata
            state_data = {
                "workflow_id": workflow_id,
                "status": status,
                "saved_at": datetime.now().isoformat(),
                "state": state
            }
            
            # Determine file path based on status
            if status == "completed":
                file_path = self.storage_path / "completed" / f"{workflow_id}.json"
            elif status == "failed":
                file_path = self.storage_path / "failed" / f"{workflow_id}.json"
            elif status == "archived":
                file_path = self.storage_path / "archived" / f"{workflow_id}.json"
            else:
                file_path = self.storage_path / "active" / f"{workflow_id}.json"
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
            
            logger.info(f"Saved workflow state: {workflow_id} ({status})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save workflow state {workflow_id}: {e}")
            return False
    
    async def load_workflow_state(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow state from disk"""
        try:
            # Search in all directories
            for status_dir in ["active", "completed", "failed", "archived"]:
                file_path = self.storage_path / status_dir / f"{workflow_id}.json"
                if file_path.exists():
                    with open(file_path, 'r') as f:
                        state_data = json.load(f)
                    
                    logger.info(f"Loaded workflow state: {workflow_id} ({state_data.get('status')})")
                    return state_data
            
            logger.warning(f"Workflow state not found: {workflow_id}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load workflow state {workflow_id}: {e}")
            return None
    
    async def list_workflows(self, status: str = None) -> List[Dict[str, Any]]:
        """List all workflows or workflows of a specific status"""
        try:
            workflows = []
            
            if status:
                # List specific status
                status_dir = self.storage_path / status
                if status_dir.exists():
                    for file_path in status_dir.glob("*.json"):
                        workflow_data = await self._load_workflow_file(file_path)
                        if workflow_data:
                            workflows.append(workflow_data)
            else:
                # List all workflows
                for status_dir in ["active", "completed", "failed", "archived"]:
                    dir_path = self.storage_path / status_dir
                    if dir_path.exists():
                        for file_path in dir_path.glob("*.json"):
                            workflow_data = await self._load_workflow_file(file_path)
                            if workflow_data:
                                workflows.append(workflow_data)
            
            # Sort by saved_at timestamp
            workflows.sort(key=lambda x: x.get("saved_at", ""), reverse=True)
            
            logger.info(f"Listed {len(workflows)} workflows")
            return workflows
            
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return []
    
    async def _load_workflow_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load workflow data from a single file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load workflow file {file_path}: {e}")
            return None
    
    async def update_workflow_status(self, workflow_id: str, new_status: str) -> bool:
        """Update workflow status and move file to appropriate directory"""
        try:
            # Find current workflow file
            current_file = None
            current_status = None
            
            for status_dir in ["active", "completed", "failed", "archived"]:
                file_path = self.storage_path / status_dir / f"{workflow_id}.json"
                if file_path.exists():
                    current_file = file_path
                    current_status = status_dir
                    break
            
            if not current_file:
                logger.warning(f"Workflow not found for status update: {workflow_id}")
                return False
            
            # Load current state
            with open(current_file, 'r') as f:
                state_data = json.load(f)
            
            # Update status
            state_data["status"] = new_status
            state_data["updated_at"] = datetime.now().isoformat()
            
            # Determine new file path
            if new_status == "completed":
                new_file_path = self.storage_path / "completed" / f"{workflow_id}.json"
            elif new_status == "failed":
                new_file_path = self.storage_path / "failed" / f"{workflow_id}.json"
            elif new_status == "archived":
                new_file_path = self.storage_path / "archived" / f"{workflow_id}.json"
            else:
                new_file_path = self.storage_path / "active" / f"{workflow_id}.json"
            
            # Save to new location
            with open(new_file_path, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
            
            # Remove old file
            if new_file_path != current_file:
                current_file.unlink()
            
            logger.info(f"Updated workflow status: {workflow_id} {current_status} -> {new_status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update workflow status {workflow_id}: {e}")
            return False
    
    async def archive_workflow(self, workflow_id: str) -> bool:
        """Archive a completed workflow"""
        try:
            return await self.update_workflow_status(workflow_id, "archived")
        except Exception as e:
            logger.error(f"Failed to archive workflow {workflow_id}: {e}")
            return False
    
    async def cleanup_old_workflows(self, days_to_keep: int = 30) -> int:
        """Clean up old archived workflows"""
        try:
            cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
            cleaned_count = 0
            
            archived_dir = self.storage_path / "archived"
            if archived_dir.exists():
                for file_path in archived_dir.glob("*.json"):
                    try:
                        with open(file_path, 'r') as f:
                            workflow_data = json.load(f)
                        
                        saved_timestamp = datetime.fromisoformat(workflow_data.get("saved_at", "1970-01-01")).timestamp()
                        
                        if saved_timestamp < cutoff_date:
                            file_path.unlink()
                            cleaned_count += 1
                            logger.debug(f"Cleaned up old workflow: {file_path.name}")
                    
                    except Exception as e:
                        logger.error(f"Failed to process workflow file {file_path}: {e}")
            
            logger.info(f"Cleaned up {cleaned_count} old workflows")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old workflows: {e}")
            return 0
    
    async def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored workflows"""
        try:
            stats = {
                "active": 0,
                "completed": 0,
                "failed": 0,
                "archived": 0,
                "total": 0
            }
            
            for status_dir in ["active", "completed", "failed", "archived"]:
                dir_path = self.storage_path / status_dir
                if dir_path.exists():
                    count = len(list(dir_path.glob("*.json")))
                    stats[status_dir] = count
                    stats["total"] += count
            
            # Add storage info
            stats["storage_path"] = str(self.storage_path)
            stats["generated_at"] = datetime.now().isoformat()
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get workflow statistics: {e}")
            return {"error": str(e)}
    
    async def export_workflow(self, workflow_id: str, export_path: str = None) -> str:
        """Export a workflow to a file"""
        try:
            workflow_data = await self.load_workflow_state(workflow_id)
            if not workflow_data:
                return ""
            
            if export_path:
                with open(export_path, 'w') as f:
                    json.dump(workflow_data, f, indent=2, default=str)
                logger.info(f"Exported workflow {workflow_id} to {export_path}")
                return export_path
            else:
                return json.dumps(workflow_data, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to export workflow {workflow_id}: {e}")
            return ""
    
    async def import_workflow(self, workflow_data: Dict[str, Any]) -> bool:
        """Import a workflow from data"""
        try:
            workflow_id = workflow_data.get("workflow_id")
            if not workflow_id:
                logger.error("No workflow_id in import data")
                return False
            
            # Save imported workflow
            status = workflow_data.get("status", "active")
            return await self.save_workflow_state(workflow_id, workflow_data.get("state", {}), status)
            
        except Exception as e:
            logger.error(f"Failed to import workflow: {e}")
            return False 