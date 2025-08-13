"""
Editor Agent for AI Agents System
Handles content quality control, fact-checking, and editing
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
from openai import OpenAI
import os

from app.core import BaseAgent, AgentType
from .tools import EditingTools

logger = structlog.get_logger()

class EditorAgent(BaseAgent):
    """Editor Agent for quality control and content editing"""
    
    def __init__(self, agent_id: str, name: str = "Editor Agent"):
        super().__init__(agent_id, AgentType.EDITOR, name)
        
        # Initialize OpenAI client if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
        else:
            self.openai_client = None
            logger.warning("No OpenAI API key provided, using fallback mode")
        
        self.editing_tools = EditingTools()
        self.quality_threshold = 0.8
        self.max_editing_rounds = 3
        
        logger.info(f"Editor Agent {name} initialized")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute editing task"""
        try:
            content = context.get("content", "")
            topic = context.get("topic", "Unknown topic")
            research_data = context.get("research_data", {})
            target_quality = context.get("target_quality", 0.9)
            editing_style = context.get("editing_style", "comprehensive")
            
            await self.start_task(f"Editing content about: {topic}")
            
            # Phase 1: Content analysis
            await self.update_progress(0.2, "Analyzing content quality")
            analysis_result = await self._analyze_content_quality(content, topic, research_data)
            
            # Phase 2: Fact-checking
            await self.update_progress(0.4, "Fact-checking content")
            fact_check_result = await self._fact_check_content(content, research_data)
            
            # Phase 3: Content editing
            await self.update_progress(0.6, "Editing and improving content")
            edited_content = await self._edit_content(content, analysis_result, fact_check_result, editing_style)
            
            # Phase 4: Final review
            await self.update_progress(0.8, "Final quality review")
            final_quality = await self._final_quality_review(edited_content, topic, research_data)
            
            # Phase 5: Generate editing report
            await self.update_progress(0.9, "Generating editing report")
            editing_report = await self._generate_editing_report(
                analysis_result, fact_check_result, final_quality, editing_style
            )
            
            # Store editing results in memory
            await self._store_editing_results(topic, edited_content, editing_report)
            
            await self.update_progress(1.0, "Editing completed")
            await self.complete_task({
                "topic": topic,
                "original_content_length": len(content),
                "edited_content_length": len(edited_content),
                "quality_improvement": final_quality - analysis_result.get("overall_quality", 0),
                "editing_style": editing_style
            })
            
            return {
                "status": "success",
                "topic": topic,
                "edited_content": edited_content,
                "original_content": content,
                "quality_score": final_quality,
                "editing_report": editing_report,
                "improvements_made": len(editing_report.get("improvements", [])),
                "editing_style": editing_style
            }
            
        except Exception as e:
            logger.error(f"Editing execution failed: {e}")
            await self.handle_error(e, "editing execution")
            return {"status": "error", "error": str(e)}
    
    async def _analyze_content_quality(self, content: str, topic: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall content quality"""
        try:
            logger.info(f"Analyzing content quality for topic: {topic}")
            
            # Use editing tools for analysis
            quality_metrics = await self.editing_tools.analyze_content_quality(content, topic)
            
            # Calculate overall quality score
            overall_quality = self._calculate_overall_quality(quality_metrics)
            
            analysis_result = {
                "overall_quality": overall_quality,
                "quality_metrics": quality_metrics,
                "topic_relevance": quality_metrics.get("topic_relevance", 0.0),
                "readability_score": quality_metrics.get("readability_score", 0.0),
                "structure_quality": quality_metrics.get("structure_quality", 0.0),
                "content_completeness": quality_metrics.get("content_completeness", 0.0)
            }
            
            # Store analysis in memory
            await self.store_memory(
                f"Content quality analysis for {topic}: {overall_quality:.2f}",
                "quality_analysis",
                0.7,
                {"topic": topic, "overall_quality": overall_quality, "metrics": quality_metrics}
            )
            
            logger.info(f"Content quality analysis completed: {overall_quality:.2f}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Content quality analysis failed: {e}")
            return {"overall_quality": 0.5, "quality_metrics": {}, "error": str(e)}
    
    def _calculate_overall_quality(self, quality_metrics: Dict[str, Any]) -> float:
        """Calculate overall quality score from individual metrics"""
        try:
            weights = {
                "topic_relevance": 0.25,
                "readability_score": 0.20,
                "structure_quality": 0.25,
                "content_completeness": 0.20,
                "grammar_quality": 0.10
            }
            
            total_score = 0.0
            total_weight = 0.0
            
            for metric, weight in weights.items():
                if metric in quality_metrics:
                    total_score += quality_metrics[metric] * weight
                    total_weight += weight
            
            if total_weight > 0:
                return total_score / total_weight
            else:
                return 0.5
                
        except Exception as e:
            logger.error(f"Overall quality calculation failed: {e}")
            return 0.5
    
    async def _fact_check_content(self, content: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fact-check content against research data"""
        try:
            logger.info("Fact-checking content against research data")
            
            # If research_data is empty or has no insights/sources, skip fact-checking
            if not research_data or not research_data.get("insights") and not research_data.get("sources"):
                logger.info("No research data available, skipping fact-checking")
                return {"accuracy_score": 1.0, "issues": [], "skipped": True}
            
            # Use editing tools for fact-checking
            fact_check_result = await self.editing_tools.fact_check_content(content, research_data)
            
            # Store fact-check results in memory
            await self.store_memory(
                f"Fact-check completed: {fact_check_result.get('accuracy_score', 0):.2f} accuracy",
                "fact_check",
                0.8,
                {"accuracy_score": fact_check_result.get("accuracy_score", 0), "issues_found": len(fact_check_result.get("issues", []))}
            )
            
            logger.info(f"Fact-check completed: {fact_check_result.get('accuracy_score', 0):.2f} accuracy")
            return fact_check_result
            
        except Exception as e:
            logger.error(f"Fact-checking failed: {e}")
            return {"accuracy_score": 0.5, "issues": [], "error": str(e)}
    
    async def _edit_content(self, content: str, analysis_result: Dict[str, Any], 
                           fact_check_result: Dict[str, Any], editing_style: str) -> str:
        """Edit and improve content based on analysis and fact-check results"""
        try:
            logger.info(f"Editing content with {editing_style} style")
            
            edited_content = content
            
            # Apply improvements based on analysis
            if analysis_result.get("overall_quality", 0) < self.quality_threshold:
                edited_content = await self.editing_tools.improve_content_structure(
                    edited_content, analysis_result.get("quality_metrics", {})
                )
            
            # Fix fact-check issues
            if fact_check_result.get("issues"):
                edited_content = await self.editing_tools.correct_factual_errors(
                    edited_content, fact_check_result.get("issues", [])
                )
            
            # Apply style-specific editing
            edited_content = await self.editing_tools.apply_editing_style(
                edited_content, editing_style
            )
            
            # Final polish
            edited_content = await self.editing_tools.polish_content(edited_content)
            
            logger.info(f"Content editing completed: {len(edited_content)} characters")
            return edited_content
            
        except Exception as e:
            logger.error(f"Content editing failed: {e}")
            return content  # Return original if editing fails
    
    async def _final_quality_review(self, content: str, topic: str, research_data: Dict[str, Any]) -> float:
        """Perform final quality review of edited content"""
        try:
            logger.info("Performing final quality review")
            
            # Re-analyze quality after editing
            final_metrics = await self.editing_tools.analyze_content_quality(content, topic)
            final_quality = self._calculate_overall_quality(final_metrics)
            
            # Store final quality in memory
            await self.store_memory(
                f"Final quality review for {topic}: {final_quality:.2f}",
                "final_quality",
                0.9,
                {"topic": topic, "final_quality": final_quality, "metrics": final_metrics}
            )
            
            logger.info(f"Final quality review completed: {final_quality:.2f}")
            return final_quality
            
        except Exception as e:
            logger.error(f"Final quality review failed: {e}")
            return 0.5
    
    async def _generate_editing_report(self, analysis_result: Dict[str, Any], 
                                     fact_check_result: Dict[str, Any], 
                                     final_quality: float, editing_style: str) -> Dict[str, Any]:
        """Generate comprehensive editing report"""
        try:
            logger.info("Generating editing report")
            
            original_quality = analysis_result.get("overall_quality", 0)
            quality_improvement = final_quality - original_quality
            
            # Identify key improvements
            improvements = []
            if quality_improvement > 0.1:
                improvements.append("Significant quality improvement achieved")
            if fact_check_result.get("issues"):
                improvements.append(f"Corrected {len(fact_check_result['issues'])} factual issues")
            if analysis_result.get("structure_quality", 0) < 0.7:
                improvements.append("Content structure improved")
            
            # Generate recommendations
            recommendations = self._generate_recommendations(analysis_result, fact_check_result, final_quality)
            
            report = {
                "editing_summary": {
                    "original_quality": original_quality,
                    "final_quality": final_quality,
                    "quality_improvement": quality_improvement,
                    "editing_style": editing_style
                },
                "quality_metrics": analysis_result.get("quality_metrics", {}),
                "fact_check_results": fact_check_result,
                "improvements": improvements,
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info("Editing report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Editing report generation failed: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def _generate_recommendations(self, analysis_result: Dict[str, Any], 
                                fact_check_result: Dict[str, Any], final_quality: float) -> List[str]:
        """Generate recommendations for further improvement"""
        try:
            recommendations = []
            
            # Quality-based recommendations
            if final_quality < 0.8:
                recommendations.append("Consider additional research to improve content depth")
                recommendations.append("Review content structure for better flow")
            
            if analysis_result.get("readability_score", 0) < 0.7:
                recommendations.append("Simplify complex sentences for better readability")
                recommendations.append("Use shorter paragraphs for easier scanning")
            
            if fact_check_result.get("accuracy_score", 0) < 0.8:
                recommendations.append("Verify all statistics and claims with primary sources")
                recommendations.append("Add more citations for factual statements")
            
            # Style recommendations
            if not recommendations:
                recommendations.append("Content meets quality standards")
                recommendations.append("Consider adding visual elements or examples")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendations generation failed: {e}")
            return ["Review content for potential improvements"]
    
    async def _store_editing_results(self, topic: str, edited_content: str, editing_report: Dict[str, Any]):
        """Store comprehensive editing results in memory"""
        try:
            # Store editing overview
            await self.store_memory(
                f"Editing completed for {topic}. Quality: {editing_report.get('editing_summary', {}).get('final_quality', 0):.2f}",
                "editing_overview",
                0.8,
                {
                    "topic": topic,
                    "final_quality": editing_report.get("editing_summary", {}).get("final_quality", 0),
                    "improvements_count": len(editing_report.get("improvements", [])),
                    "recommendations_count": len(editing_report.get("recommendations", []))
                }
            )
            
            logger.info(f"Stored editing results for topic: {topic}")
            
        except Exception as e:
            logger.error(f"Failed to store editing results: {e}")
    
    async def get_editing_history(self, topic: str = None) -> List[Dict[str, Any]]:
        """Get editing history from memory"""
        try:
            if topic:
                memories = await self.retrieve_memories(topic, "editing_overview")
            else:
                memories = await self.retrieve_memories(memory_type="editing_overview")
            
            return [
                {
                    "content": memory.content,
                    "metadata": memory.metadata,
                    "created_at": memory.created_at.isoformat(),
                    "importance": memory.importance_score
                }
                for memory in memories
            ]
            
        except Exception as e:
            logger.error(f"Failed to get editing history: {e}")
            return []
    
    async def review_specific_section(self, content: str, section: str, 
                                    research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Review a specific section of content"""
        try:
            logger.info(f"Reviewing specific section: {section}")
            
            # Extract section content
            section_content = self._extract_section_content(content, section)
            if not section_content:
                return {"error": f"Section '{section}' not found in content"}
            
            # Analyze section quality
            section_quality = await self.editing_tools.analyze_section_quality(section_content, section)
            
            # Fact-check section
            section_facts = await self.editing_tools.fact_check_section(section_content, research_data)
            
            # Generate section-specific recommendations
            recommendations = self._generate_section_recommendations(section_quality, section_facts)
            
            return {
                "section": section,
                "content": section_content,
                "quality_analysis": section_quality,
                "fact_check": section_facts,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Section review failed: {e}")
            return {"error": str(e)}
    
    def _extract_section_content(self, content: str, section: str) -> str:
        """Extract content for a specific section"""
        try:
            # Simple section extraction based on headers
            import re
            
            # Look for section headers (## or ###)
            pattern = rf"##\s*{re.escape(section)}.*?\n(.*?)(?=##|$)"
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            
            if match:
                return match.group(1).strip()
            else:
                # Try alternative patterns
                patterns = [
                    rf"###\s*{re.escape(section)}.*?\n(.*?)(?=##|###|$)",
                    rf"#\s*{re.escape(section)}.*?\n(.*?)(?=#|$)"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
                    if match:
                        return match.group(1).strip()
            
            return ""
            
        except Exception as e:
            logger.error(f"Section extraction failed: {e}")
            return ""
    
    def _generate_section_recommendations(self, section_quality: Dict[str, Any], 
                                        section_facts: Dict[str, Any]) -> List[str]:
        """Generate recommendations for a specific section"""
        try:
            recommendations = []
            
            # Quality-based recommendations
            if section_quality.get("readability_score", 0) < 0.7:
                recommendations.append("Simplify sentence structure for better readability")
            
            if section_quality.get("content_depth", 0) < 0.6:
                recommendations.append("Add more detailed explanations and examples")
            
            # Fact-based recommendations
            if section_facts.get("accuracy_score", 0) < 0.8:
                recommendations.append("Verify factual claims with additional sources")
            
            if not recommendations:
                recommendations.append("Section meets quality standards")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Section recommendations generation failed: {e}")
            return ["Review section for potential improvements"]
