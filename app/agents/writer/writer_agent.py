"""
Writer Agent for AI Agents System
Handles content generation, structuring, and optimization
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
from openai import OpenAI
import os

from app.core import BaseAgent, AgentType
from .tools import WritingTools

logger = structlog.get_logger()

class WriterAgent(BaseAgent):
    """Writer Agent for generating and optimizing content"""
    
    def __init__(self, agent_id: str, name: str = "Writer Agent"):
        super().__init__(agent_id, AgentType.WRITER, name)
        
        # Initialize OpenAI client if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
        else:
            self.openai_client = None
            logger.warning("No OpenAI API key provided, using fallback mode")
        
        self.writing_tools = WritingTools()
        self.max_iterations = 3
        self.quality_threshold = 0.8
        
        logger.info(f"Writer Agent {name} initialized")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute writing task"""
        try:
            topic = context.get("topic", "Unknown topic")
            target_length = context.get("target_length", 1500)
            research_data = context.get("research_data", {})
            writing_style = context.get("writing_style", "professional")
            
            await self.start_task(f"Writing content about: {topic}")
            
            # Phase 1: Content planning
            await self.update_progress(0.2, "Planning content structure")
            content_plan = await self._create_content_plan(topic, target_length, research_data)
            
            # Phase 2: Initial content generation
            await self.update_progress(0.4, "Generating initial content")
            initial_content = await self._generate_initial_content(topic, content_plan, research_data, writing_style)
            
            # Phase 3: Content optimization
            await self.update_progress(0.7, "Optimizing content")
            optimized_content = await self._optimize_content(initial_content, target_length, writing_style)
            
            # Phase 4: Final review and formatting
            await self.update_progress(0.9, "Final review and formatting")
            final_content = await self._finalize_content(optimized_content, topic, writing_style)
            
            # Store writing results in memory
            await self._store_writing_results(topic, final_content, content_plan)
            
            await self.update_progress(1.0, "Writing completed")
            await self.complete_task({
                "topic": topic,
                "content": final_content,
                "word_count": len(final_content.split()),
                "content_plan": content_plan,
                "writing_style": writing_style
            })
            
            return {
                "status": "success",
                "topic": topic,
                "content": final_content,
                "word_count": len(final_content.split()),
                "writing_style": writing_style,
                "quality_score": self._calculate_content_quality(final_content, content_plan)
            }
            
        except Exception as e:
            logger.error(f"Writing execution failed: {e}")
            await self.handle_error(e, "writing execution")
            return {"status": "error", "error": str(e)}
    
    async def _create_content_plan(self, topic: str, target_length: int, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a structured content plan"""
        try:
            logger.info(f"Creating content plan for topic: {topic}")
            
            # Extract key insights from research
            insights = research_data.get("insights", [])
            sources = research_data.get("sources", [])
            
            # Use writing tools to create structure
            content_structure = await self.writing_tools.create_content_structure(
                topic, target_length, insights, sources
            )
            
            # Store plan in memory
            await self.store_memory(
                f"Content plan for {topic}: {content_structure}",
                "content_plan",
                0.8,
                {"topic": topic, "target_length": target_length, "insights_count": len(insights)}
            )
            
            logger.info(f"Content plan created: {len(content_structure)} sections")
            return content_structure
            
        except Exception as e:
            logger.error(f"Content planning failed: {e}")
            # Fallback to basic structure
            return self._create_fallback_content_plan(topic, target_length)
    
    def _create_fallback_content_plan(self, topic: str, target_length: int) -> Dict[str, Any]:
        """Create a fallback content plan"""
        try:
            # Basic structure based on target length
            sections = []
            words_per_section = target_length // 4  # 4 main sections
            
            sections.extend([
                {
                    "title": "Introduction",
                    "purpose": "Introduce the topic and set context",
                    "target_words": words_per_section,
                    "key_points": ["Topic overview", "Relevance", "Scope"]
                },
                {
                    "title": "Main Content",
                    "purpose": "Present core information and insights",
                    "target_words": words_per_section * 2,
                    "key_points": ["Key concepts", "Evidence", "Examples"]
                },
                {
                    "title": "Analysis",
                    "purpose": "Analyze implications and provide insights",
                    "target_words": words_per_section,
                    "key_points": ["Trends", "Challenges", "Opportunities"]
                },
                {
                    "title": "Conclusion",
                    "purpose": "Summarize and provide actionable takeaways",
                    "target_words": words_per_section,
                    "key_points": ["Summary", "Recommendations", "Future outlook"]
                }
            ])
            
            return {
                "topic": topic,
                "target_length": target_length,
                "sections": sections,
                "writing_approach": "structured",
                "fallback": True
            }
        except Exception as e:
            logger.error(f"Fallback content plan creation failed: {e}")
            return {"topic": topic, "target_length": target_length, "sections": []}
    
    async def _generate_initial_content(self, topic: str, content_plan: Dict[str, Any], 
                                      research_data: Dict[str, Any], writing_style: str) -> str:
        """Generate initial content based on plan and research"""
        try:
            logger.info(f"Generating initial content for topic: {topic}")
            
            if not self.openai_client:
                logger.info("OpenAI client not available, using fallback content generation")
                return await self._generate_fallback_content(topic, content_plan, research_data, writing_style)
            
            # Use GPT to generate content
            prompt = self._create_content_generation_prompt(topic, content_plan, research_data, writing_style)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional content writer expert at creating engaging, informative content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=content_plan.get("target_length", 1500) * 2,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            # Store initial content in memory
            await self.store_memory(
                f"Initial content for {topic}: {content[:200]}...",
                "initial_content",
                0.6,
                {"topic": topic, "writing_style": writing_style, "word_count": len(content.split())}
            )
            
            logger.info(f"Generated initial content: {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"Initial content generation failed: {e}")
            return await self._generate_fallback_content(topic, content_plan, research_data, writing_style)
    
    async def _generate_fallback_content(self, topic: str, content_plan: Dict[str, Any], 
                                       research_data: Dict[str, Any], writing_style: str) -> str:
        """Generate fallback content using templates"""
        try:
            logger.info(f"Generating fallback content for topic: {topic}")
            
            content_parts = []
            
            # Generate content for each section
            for section in content_plan.get("sections", []):
                section_title = section.get("title", "Section")
                section_content = await self.writing_tools.generate_section_content(
                    topic, section, research_data, writing_style
                )
                content_parts.append(f"## {section_title}\n\n{section_content}\n\n")
            
            content = "\n".join(content_parts)
            
            # Store fallback content in memory
            await self.store_memory(
                f"Fallback content for {topic}: {content[:200]}...",
                "fallback_content",
                0.5,
                {"topic": topic, "writing_style": writing_style, "fallback": True}
            )
            
            logger.info(f"Generated fallback content: {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"Fallback content generation failed: {e}")
            return f"Content about {topic} could not be generated due to technical issues."
    
    def _create_content_generation_prompt(self, topic: str, content_plan: Dict[str, Any], 
                                        research_data: Dict[str, Any], writing_style: str) -> str:
        """Create prompt for content generation"""
        insights = research_data.get("insights", [])
        sources = research_data.get("sources", [])
        
        prompt = f"""
        Topic: {topic}
        Writing Style: {writing_style}
        Target Length: {content_plan.get('target_length', 1500)} words
        
        Content Structure:
        {self._format_content_plan(content_plan)}
        
        Key Insights from Research:
        {chr(10).join(f"- {insight}" for insight in insights[:5])}
        
        Research Sources: {len(sources)} sources available
        
        Please write comprehensive, engaging content that:
        1. Follows the specified structure
        2. Incorporates the research insights
        3. Maintains the {writing_style} writing style
        4. Is approximately {content_plan.get('target_length', 1500)} words
        5. Includes relevant examples and evidence
        6. Has clear transitions between sections
        7. Ends with actionable conclusions
        
        Format as a well-structured article with clear headings.
        """
        
        return prompt
    
    def _format_content_plan(self, content_plan: Dict[str, Any]) -> str:
        """Format content plan for prompt"""
        try:
            sections = content_plan.get("sections", [])
            formatted = []
            
            for section in sections:
                formatted.append(f"- {section.get('title', 'Section')}: {section.get('purpose', 'Purpose')}")
            
            return "\n".join(formatted)
            
        except Exception as e:
            logger.error(f"Content plan formatting failed: {e}")
            return "Standard structure: Introduction, Main Content, Analysis, Conclusion"
    
    async def _optimize_content(self, content: str, target_length: int, writing_style: str) -> str:
        """Optimize content for quality and length"""
        try:
            logger.info(f"Optimizing content for {writing_style} style")
            
            # Use writing tools for optimization
            optimized = await self.writing_tools.optimize_content(content, target_length, writing_style)
            
            # Store optimization in memory
            await self.store_memory(
                f"Content optimization for {writing_style} style: {len(optimized)} characters",
                "content_optimization",
                0.7,
                {"original_length": len(content), "optimized_length": len(optimized), "style": writing_style}
            )
            
            logger.info(f"Content optimized: {len(optimized)} characters")
            return optimized
            
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            return content  # Return original if optimization fails
    
    async def _finalize_content(self, content: str, topic: str, writing_style: str) -> str:
        """Finalize content with formatting and review"""
        try:
            logger.info(f"Finalizing content for topic: {topic}")
            
            # Apply final formatting
            finalized = await self.writing_tools.finalize_content(content, topic, writing_style)
            
            # Store finalized content in memory
            await self.store_memory(
                f"Finalized content for {topic}: {finalized[:200]}...",
                "finalized_content",
                0.9,
                {"topic": topic, "writing_style": writing_style, "final_length": len(finalized)}
            )
            
            logger.info(f"Content finalized: {len(finalized)} characters")
            return finalized
            
        except Exception as e:
            logger.error(f"Content finalization failed: {e}")
            return content  # Return original if finalization fails
    
    async def _store_writing_results(self, topic: str, content: str, content_plan: Dict[str, Any]):
        """Store comprehensive writing results in memory"""
        try:
            # Store topic overview
            await self.store_memory(
                f"Writing completed for {topic}. Generated {len(content)} characters with {len(content_plan.get('sections', []))} sections.",
                "writing_overview",
                0.8,
                {"topic": topic, "content_length": len(content), "sections_count": len(content_plan.get('sections', []))}
            )
            
            logger.info(f"Stored writing results for topic: {topic}")
            
        except Exception as e:
            logger.error(f"Failed to store writing results: {e}")
    
    def _calculate_content_quality(self, content: str, content_plan: Dict[str, Any]) -> float:
        """Calculate overall content quality score"""
        try:
            if not content or not content_plan:
                return 0.0
            
            # Quality factors
            structure_quality = min(1.0, len(content_plan.get("sections", [])) / 4.0)  # 4+ sections is optimal
            content_length = len(content.split())
            target_length = content_plan.get("target_length", 1500)
            length_quality = min(1.0, content_length / target_length) if target_length > 0 else 0.5
            
            # Basic readability (simple word count per sentence)
            sentences = content.split('.')
            avg_words_per_sentence = content_length / len(sentences) if sentences else 0
            readability_quality = 1.0 if 10 <= avg_words_per_sentence <= 25 else 0.7
            
            # Weighted average
            overall_quality = (structure_quality * 0.3) + (length_quality * 0.4) + (readability_quality * 0.3)
            
            return min(1.0, overall_quality)
            
        except Exception as e:
            logger.error(f"Quality calculation failed: {e}")
            return 0.5
    
    async def get_writing_history(self, topic: str = None) -> List[Dict[str, Any]]:
        """Get writing history from memory"""
        try:
            if topic:
                memories = await self.retrieve_memories(topic, "writing_overview")
            else:
                memories = await self.retrieve_memories(memory_type="writing_overview")
            
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
            logger.error(f"Failed to get writing history: {e}")
            return [] 