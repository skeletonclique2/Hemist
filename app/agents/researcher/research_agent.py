"""
Research Agent for AI Agents System
Handles web search, content extraction, and research summarization
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog
from openai import OpenAI
import os
import google.generativeai as genai

from app.core import BaseAgent, AgentType, AgentMemory
from .tools import ResearchTools

logger = structlog.get_logger()

class ResearchAgent(BaseAgent):
    """Research Agent for gathering and analyzing information"""
    
    def __init__(self, agent_id: str, name: str = "Research Agent"):
        super().__init__(agent_id, AgentType.RESEARCHER, name)
        
        # Initialize OpenAI client if API key is available
        api_key = os.getenv("OPENAI_API_KEY")
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.openai_client = OpenAI(api_key=api_key)
        else:
            self.openai_client = None
            logger.warning("No OpenAI API key provided, using fallback mode")
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_client = genai.GenerativeModel("gemini-1.5-pro-latest")
        else:
            self.gemini_client = None
            logger.warning("No Gemini API key provided, Gemini fallback will not be available")
        
        self.research_tools = ResearchTools()
        self.max_sources = 10
        self.max_content_length = 5000  # characters per source
        
        logger.info(f"Research Agent {name} initialized")
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research task"""
        try:
            topic = context.get("topic", "Unknown topic")
            target_length = context.get("target_length", 1500)
            quality_threshold = context.get("quality_threshold", 0.8)
            
            await self.start_task(f"Researching: {topic}")
            
            # Phase 1: Initial research
            await self.update_progress(0.2, "Starting initial research")
            initial_sources = await self._conduct_initial_research(topic)
            
            # Phase 2: Deep dive into promising sources
            await self.update_progress(0.5, "Analyzing sources in detail")
            analyzed_sources = await self._analyze_sources(initial_sources, topic)
            
            # Phase 3: Extract key insights
            await self.update_progress(0.8, "Extracting key insights")
            key_insights = await self._extract_key_insights(analyzed_sources, topic)
            
            # Phase 4: Generate research summary
            await self.update_progress(0.9, "Generating research summary")
            research_summary = await self._generate_research_summary(topic, key_insights, target_length)
            
            # Store research results in memory
            await self._store_research_results(topic, analyzed_sources, key_insights, research_summary)
            
            await self.update_progress(1.0, "Research completed")
            await self.complete_task({
                "topic": topic,
                "sources": analyzed_sources,
                "insights": key_insights,
                "summary": research_summary
            })
            
            return {
                "status": "success",
                "topic": topic,
                "sources_count": len(analyzed_sources),
                "insights_count": len(key_insights),
                "summary_length": len(research_summary),
                "quality_score": self._calculate_research_quality(analyzed_sources, key_insights)
            }
            
        except Exception as e:
            logger.error(f"Research execution failed: {e}")
            await self.handle_error(e, "research execution")
            return {"status": "error", "error": str(e)}
    
    _initial_research_cache = {}

    async def _conduct_initial_research(self, topic: str) -> List[Dict[str, Any]]:
        """Conduct initial research to find relevant sources with caching"""
        try:
            if topic in self._initial_research_cache:
                logger.info(f"Using cached initial research results for topic: {topic}")
                return self._initial_research_cache[topic]
            
            logger.info(f"Starting initial research for topic: {topic}")
            
            # Use research tools to find sources
            search_results = await self.research_tools.search_web(topic, max_results=self.max_sources)
            
            # Filter and rank sources
            filtered_sources = await self._filter_sources(search_results, topic)
            
            logger.info(f"Found {len(filtered_sources)} relevant sources")
            self._initial_research_cache[topic] = filtered_sources
            return filtered_sources
            
        except Exception as e:
            logger.error(f"Initial research failed: {e}")
            return []
    
    async def _analyze_sources(self, sources: List[Dict[str, Any]], topic: str) -> List[Dict[str, Any]]:
        """Analyze sources in detail to extract content and insights"""
        try:
            logger.info(f"Analyzing {len(sources)} sources for topic: {topic}")
            
            analyzed_sources = []
            
            for i, source in enumerate(sources):
                try:
                    await self.update_progress(0.5 + (i * 0.3 / len(sources)), f"Analyzing source {i+1}/{len(sources)}")
                    
                    # Extract content from source
                    content = await self.research_tools.extract_content(source["url"])
                    
                    if content and len(content) > 100:  # Minimum content threshold
                        # Analyze content relevance
                        relevance_score = await self._analyze_content_relevance(content, topic)
                        
                        if relevance_score > 0.6:  # Relevance threshold
                            analyzed_source = {
                                **source,
                                "content": content[:self.max_content_length],
                                "relevance_score": relevance_score,
                                "word_count": len(content.split()),
                                "analyzed_at": datetime.utcnow().isoformat()
                            }
                            analyzed_sources.append(analyzed_source)
                            
                            # Store source in memory
                            await self.store_memory(
                                f"Source: {source['title']} - {content[:200]}...",
                                "research_source",
                                0.7,
                                {"url": source["url"], "relevance": relevance_score}
                            )
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze source {source.get('url', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Successfully analyzed {len(analyzed_sources)} sources")
            return analyzed_sources
            
        except Exception as e:
            logger.error(f"Source analysis failed: {e}")
            return []
    
    async def _extract_key_insights(self, sources: List[Dict[str, Any]], topic: str) -> List[str]:
        """Extract key insights from analyzed sources"""
        try:
            logger.info(f"Extracting key insights from {len(sources)} sources")
            
            if not sources:
                return []
            
            # Combine content from all sources
            combined_content = "\n\n".join([
                f"Source: {source['title']}\n{source['content']}"
                for source in sources[:5]  # Limit to top 5 sources for insight extraction
            ])
            
            # Use GPT to extract key insights
            insights = await self._generate_insights_with_gpt(topic, combined_content)
            
            # Store insights in memory
            for insight in insights:
                await self.store_memory(
                    insight,
                    "research_insight",
                    0.8,
                    {"topic": topic, "source_count": len(sources)}
                )
            
            logger.info(f"Extracted {len(insights)} key insights")
            return insights
            
        except Exception as e:
            logger.error(f"Insight extraction failed: {e}")
            return []
    
    async def _generate_insights_with_gpt(self, topic: str, content: str) -> List[str]:
        """Generate key insights using GPT or Gemini, with fallback"""
        try:
            # Check if OpenAI client is available
            if self.openai_client:
                prompt = f"""
                Topic: {topic}
                
                Content from multiple sources:
                {content[:3000]}  # Limit content length
                
                Please extract 5-7 key insights from this content. Each insight should be:
                - Specific and actionable
                - Based on the provided content
                - Relevant to the topic
                - Written in clear, concise language
                
                Format as a numbered list.
                """
                try:
                    response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "You are a research analyst expert at extracting key insights from content."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=500,
                        temperature=0.3
                    )
                    insights_text = response.choices[0].message.content
                    insights = [insight.strip() for insight in insights_text.split('\n') if insight.strip() and insight[0].isdigit()]
                    return insights
                except Exception as e:
                    logger.error(f"OpenAI GPT insight generation failed: {e}")
                    # Try Gemini fallback if available
            if self.gemini_client:
                try:
                    gemini_prompt = f"""
                    Topic: {topic}

                    Content from multiple sources:
                    {content[:3000]}

                    Please extract 5-7 key insights from this content. Each insight should be:
                    - Specific and actionable
                    - Based on the provided content
                    - Relevant to the topic
                    - Written in clear, concise language

                    Format as a numbered list.
                    """
                    gemini_response = self.gemini_client.generate_content(gemini_prompt)
                    gemini_text = gemini_response.text if hasattr(gemini_response, "text") else str(gemini_response)
                    insights = [insight.strip() for insight in gemini_text.split('\n') if insight.strip() and insight[0].isdigit()]
                    return insights
                except Exception as e:
                    logger.error(f"Gemini insight generation failed: {e}")
            logger.info("No LLM available or all LLMs failed, using fallback insight generation")
            return self._generate_fallback_insights(topic, content)
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return self._generate_fallback_insights(topic, content)
    
    async def _generate_fallback_summary(self, topic: str, insights: List[str], target_length: int) -> str:
        """Generate fallback research summary using template"""
        try:
            logger.info(f"Generating fallback summary for topic: {topic}")
            
            if not insights:
                return f"Research on {topic} did not yield sufficient insights."
            
            # Create a structured summary from insights
            summary_parts = [
                f"# Research Summary: {topic}",
                "",
                "## Overview",
                f"This research explores the topic of {topic} and provides comprehensive insights based on multiple sources.",
                "",
                "## Key Insights",
            ]
            
            # Add insights
            for i, insight in enumerate(insights, 1):
                summary_parts.append(f"{i}. {insight}")
            
            summary_parts.extend([
                "",
                "## Conclusion",
                f"Based on the research conducted, {topic} presents significant opportunities and challenges that warrant further investigation and consideration.",
                "",
                f"*This summary was generated based on {len(insights)} key insights from research sources.*"
            ])
            
            summary = "\n".join(summary_parts)
            
            # Store summary in memory
            await self.store_memory(
                summary,
                "research_summary",
                0.7,  # Lower importance for fallback summaries
                {"topic": topic, "insights_count": len(insights), "target_length": target_length, "fallback": True}
            )
            
            logger.info(f"Generated fallback summary: {len(summary)} characters")
            return summary
            
        except Exception as e:
            logger.error(f"Fallback summary generation failed: {e}")
            return f"Research summary for {topic}: {len(insights)} insights were identified and analyzed."
    
    def _generate_fallback_insights(self, topic: str, content: str) -> List[str]:
        """Generate fallback insights using simple text analysis"""
        try:
            # Simple keyword frequency analysis
            words = content.lower().split()
            word_freq = {}
            
            # Filter out common words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            
            for word in words:
                if word.isalpha() and word not in stop_words and len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top keywords
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Generate simple insights
            insights = []
            for keyword, freq in top_keywords[:5]:
                insights.append(f"{keyword.title()} is a key concept related to {topic}")
            
            return insights
            
        except Exception as e:
            logger.error(f"Fallback insight generation failed: {e}")
            return [f"Research on {topic} revealed important information", f"Multiple sources discuss {topic}"]
    
    async def _generate_research_summary(self, topic: str, insights: List[str], target_length: int) -> str:
        """Generate a comprehensive research summary"""
        try:
            logger.info(f"Generating research summary for topic: {topic}")
            
            if not insights:
                return f"Research on {topic} did not yield sufficient insights."
            
            # Check if OpenAI client is available
            if not self.openai_client:
                logger.info("OpenAI client not available, using fallback summary generation")
                return await self._generate_fallback_summary(topic, insights, target_length)
            
            prompt = f"""
            Topic: {topic}
            Target Length: {target_length} words
            
            Key Insights:
            {chr(10).join(f"- {insight}" for insight in insights)}
            
            Please write a comprehensive research summary that:
            1. Introduces the topic clearly
            2. Synthesizes the key insights
            3. Provides actionable conclusions
            4. Maintains academic/professional tone
            5. Is approximately {target_length} words
            
            Format as a well-structured article with clear sections.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional research writer expert at creating comprehensive summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=target_length * 2,  # Allow for longer generation
                temperature=0.4
            )
            
            summary = response.choices[0].message.content
            
            # Store summary in memory
            await self.store_memory(
                summary,
                "research_summary",
                0.9,
                {"topic": topic, "insights_count": len(insights), "target_length": target_length}
            )
            
            logger.info(f"Generated research summary: {len(summary)} characters")
            return summary
            
        except Exception as e:
            logger.error(f"Research summary generation failed: {e}")
            return f"Research summary generation failed: {str(e)}"
    
    async def _filter_sources(self, sources: List[Dict[str, Any]], topic: str) -> List[Dict[str, Any]]:
        """Filter and rank sources by relevance and quality"""
        try:
            if not sources:
                return []
            
            # Simple relevance scoring based on title and description
            scored_sources = []
            
            for source in sources:
                score = 0
                title = source.get("title", "").lower()
                description = source.get("description", "").lower()
                topic_words = topic.lower().split()
                
                # Score based on topic word matches
                for word in topic_words:
                    if word in title:
                        score += 3
                    if word in description:
                        score += 2
                
                # Bonus for recent sources
                if source.get("date"):
                    score += 1
                
                # Bonus for reputable domains
                url = source.get("url", "")
                if any(domain in url for domain in [".edu", ".gov", ".org", "wikipedia.org"]):
                    score += 2
                
                scored_sources.append({**source, "relevance_score": score})
            
            # Sort by relevance score and return top sources
            scored_sources.sort(key=lambda x: x["relevance_score"], reverse=True)
            return scored_sources[:self.max_sources]
            
        except Exception as e:
            logger.error(f"Source filtering failed: {e}")
            return sources[:self.max_sources]  # Return original list if filtering fails
    
    async def _analyze_content_relevance(self, content: str, topic: str) -> float:
        """Analyze content relevance to topic using simple heuristics"""
        try:
            content_lower = content.lower()
            topic_words = topic.lower().split()
            
            # Count topic word occurrences
            word_matches = sum(content_lower.count(word) for word in topic_words)
            
            # Calculate relevance score (0.0 to 1.0)
            relevance_score = min(1.0, word_matches / 10.0)  # Normalize
            
            return relevance_score
            
        except Exception as e:
            logger.error(f"Content relevance analysis failed: {e}")
            return 0.5  # Default neutral score
    
    def _calculate_research_quality(self, sources: List[Dict[str, Any]], insights: List[str]) -> float:
        """Calculate overall research quality score"""
        try:
            if not sources or not insights:
                return 0.0
            
            # Quality factors
            source_quality = sum(source.get("relevance_score", 0) for source in sources) / len(sources)
            insight_quality = min(1.0, len(insights) / 5.0)  # 5+ insights is optimal
            
            # Weighted average
            overall_quality = (source_quality * 0.6) + (insight_quality * 0.4)
            
            return min(1.0, overall_quality)
            
        except Exception as e:
            logger.error(f"Quality calculation failed: {e}")
            return 0.5
    
    async def _store_research_results(self, topic: str, sources: List[Dict[str, Any]], 
                                    insights: List[str], summary: str):
        """Store comprehensive research results in memory"""
        try:
            # Store topic overview
            await self.store_memory(
                f"Research completed on {topic}. Found {len(sources)} sources and {len(insights)} insights.",
                "research_overview",
                0.8,
                {"topic": topic, "sources_count": len(sources), "insights_count": len(insights)}
            )
            
            # Store source summaries
            for source in sources[:3]:  # Store top 3 sources
                await self.store_memory(
                    f"Source: {source['title']} - {source['content'][:100]}...",
                    "research_source_detail",
                    0.6,
                    {"url": source.get("url"), "relevance": source.get("relevance_score", 0)}
                )
            
            logger.info(f"Stored research results for topic: {topic}")
            
        except Exception as e:
            logger.error(f"Failed to store research results: {e}")
    
    async def get_research_history(self, topic: str = None) -> List[Dict[str, Any]]:
        """Get research history from memory"""
        try:
            if topic:
                memories = await self.retrieve_memories(topic, "research_overview")
            else:
                memories = await self.retrieve_memories(memory_type="research_overview")
            
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
            logger.error(f"Failed to get research history: {e}")
            return []
