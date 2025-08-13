"""
Writing Tools for AI Agents System
Provides content structuring, optimization, and formatting capabilities
"""

import re
from typing import Dict, Any, List, Optional
import structlog
from textstat import textstat

logger = structlog.get_logger()

class WritingTools:
    """Tools for content writing, structuring, and optimization"""
    
    def __init__(self):
        logger.info("WritingTools initialized")
    
    async def create_content_structure(self, topic: str, target_length: int, 
                                    insights: List[str], sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a structured content plan"""
        try:
            logger.info(f"Creating content structure for topic: {topic}")
            
            # Calculate section distribution based on target length
            sections = self._calculate_section_distribution(target_length, len(insights))
            
            # Create section details
            section_details = []
            for i, section in enumerate(sections):
                section_details.append({
                    "title": section["title"],
                    "purpose": section["purpose"],
                    "target_words": section["words"],
                    "key_points": self._extract_key_points_for_section(section, insights, i),
                    "insights_count": section.get("insights_count", 0)
                })
            
            structure = {
                "topic": topic,
                "target_length": target_length,
                "sections": section_details,
                "writing_approach": "structured",
                "insights_coverage": len(insights),
                "sources_count": len(sources),
                "estimated_reading_time": self._estimate_reading_time(target_length)
            }
            
            logger.info(f"Content structure created with {len(section_details)} sections")
            return structure
            
        except Exception as e:
            logger.error(f"Content structure creation failed: {e}")
            return self._create_basic_structure(topic, target_length)
    
    def _calculate_section_distribution(self, target_length: int, insights_count: int) -> List[Dict[str, Any]]:
        """Calculate word distribution across sections"""
        try:
            # Standard section distribution
            sections = [
                {"title": "Introduction", "purpose": "Introduce topic and set context", "words": int(target_length * 0.15)},
                {"title": "Main Content", "purpose": "Present core information and insights", "words": int(target_length * 0.6)},
                {"title": "Analysis", "purpose": "Analyze implications and provide insights", "words": int(target_length * 0.15)},
                {"title": "Conclusion", "purpose": "Summarize and provide actionable takeaways", "words": int(target_length * 0.1)}
            ]
            
            # Adjust based on insights count
            if insights_count > 10:
                # Add more detailed sections for complex topics
                sections.insert(2, {"title": "Detailed Analysis", "purpose": "Deep dive into key insights", "words": int(target_length * 0.2)})
                # Adjust other sections
                sections[1]["words"] = int(target_length * 0.4)  # Main content
                sections[3]["words"] = int(target_length * 0.1)  # Analysis
                sections[4]["words"] = int(target_length * 0.1)  # Conclusion
            
            return sections
            
        except Exception as e:
            logger.error(f"Section distribution calculation failed: {e}")
            return [
                {"title": "Introduction", "purpose": "Introduce topic", "words": int(target_length * 0.2)},
                {"title": "Main Content", "purpose": "Core information", "words": int(target_length * 0.6)},
                {"title": "Conclusion", "purpose": "Summary", "words": int(target_length * 0.2)}
            ]
    
    def _extract_key_points_for_section(self, section: Dict[str, Any], insights: List[str], section_index: int) -> List[str]:
        """Extract relevant key points for a specific section"""
        try:
            if not insights:
                return ["Key point 1", "Key point 2", "Key point 3"]
            
            # Distribute insights across sections
            insights_per_section = max(1, len(insights) // 4)
            start_idx = section_index * insights_per_section
            end_idx = start_idx + insights_per_section
            
            section_insights = insights[start_idx:end_idx]
            
            # If no insights for this section, provide generic points
            if not section_insights:
                if section["title"] == "Introduction":
                    return ["Topic overview", "Relevance", "Scope"]
                elif section["title"] == "Main Content":
                    return ["Key concepts", "Evidence", "Examples"]
                elif section["title"] == "Analysis":
                    return ["Trends", "Challenges", "Opportunities"]
                elif section["title"] == "Conclusion":
                    return ["Summary", "Recommendations", "Future outlook"]
                else:
                    return ["Key point 1", "Key point 2", "Key point 3"]
            
            return section_insights[:3]  # Limit to 3 key points per section
            
        except Exception as e:
            logger.error(f"Key points extraction failed: {e}")
            return ["Key point 1", "Key point 2", "Key point 3"]
    
    def _create_basic_structure(self, topic: str, target_length: int) -> Dict[str, Any]:
        """Create a basic content structure as fallback"""
        try:
            return {
                "topic": topic,
                "target_length": target_length,
                "sections": [
                    {
                        "title": "Introduction",
                        "purpose": "Introduce the topic",
                        "target_words": int(target_length * 0.2),
                        "key_points": ["Overview", "Context", "Scope"],
                        "insights_count": 0
                    },
                    {
                        "title": "Main Content",
                        "purpose": "Core information",
                        "target_words": int(target_length * 0.6),
                        "key_points": ["Key concepts", "Details", "Examples"],
                        "insights_count": 0
                    },
                    {
                        "title": "Conclusion",
                        "purpose": "Summary and takeaways",
                        "target_words": int(target_length * 0.2),
                        "key_points": ["Summary", "Key points", "Next steps"],
                        "insights_count": 0
                    }
                ],
                "writing_approach": "basic",
                "insights_coverage": 0,
                "sources_count": 0,
                "estimated_reading_time": self._estimate_reading_time(target_length)
            }
            
        except Exception as e:
            logger.error(f"Basic structure creation failed: {e}")
            return {"topic": topic, "target_length": target_length, "sections": []}
    
    def _estimate_reading_time(self, word_count: int) -> str:
        """Estimate reading time in minutes"""
        try:
            # Average reading speed: 200-250 words per minute
            minutes = word_count / 225
            if minutes < 1:
                return "Less than 1 minute"
            elif minutes < 2:
                return "1-2 minutes"
            else:
                return f"{int(minutes)}-{int(minutes + 1)} minutes"
                
        except Exception as e:
            logger.error(f"Reading time estimation failed: {e}")
            return "Unknown"
    
    async def generate_section_content(self, topic: str, section: Dict[str, Any], 
                                     research_data: Dict[str, Any], writing_style: str) -> str:
        """Generate content for a specific section"""
        try:
            logger.info(f"Generating content for section: {section.get('title', 'Unknown')}")
            
            title = section.get("title", "Section")
            purpose = section.get("purpose", "Content purpose")
            key_points = section.get("key_points", [])
            target_words = section.get("target_words", 300)
            
            # Create section content using templates
            if title.lower() == "introduction":
                content = self._generate_introduction_section(topic, purpose, key_points, target_words, writing_style)
            elif title.lower() == "conclusion":
                content = self._generate_conclusion_section(topic, purpose, key_points, target_words, writing_style)
            else:
                content = self._generate_main_content_section(topic, title, purpose, key_points, target_words, writing_style)
            
            logger.info(f"Generated {len(content)} characters for section: {title}")
            return content
            
        except Exception as e:
            logger.error(f"Section content generation failed: {e}")
            return f"Content for {section.get('title', 'this section')} could not be generated."
    
    def _generate_introduction_section(self, topic: str, purpose: str, key_points: List[str], 
                                     target_words: int, writing_style: str) -> str:
        """Generate introduction section content"""
        try:
            # Calculate sentences needed (assuming 15-20 words per sentence)
            sentences_needed = max(3, target_words // 18)
            
            content_parts = []
            
            # Hook sentence
            content_parts.append(f"{topic} represents one of the most significant developments in modern technology.")
            
            # Context sentences
            if len(key_points) >= 2:
                content_parts.append(f"This topic encompasses {key_points[0].lower()} and addresses {key_points[1].lower()}.")
            
            # Purpose statement
            content_parts.append(f"The purpose of this discussion is to {purpose.lower()}.")
            
            # Scope and overview
            if len(key_points) >= 3:
                content_parts.append(f"We will explore {key_points[2].lower()} and provide comprehensive insights.")
            
            # Additional context to reach target length
            remaining_sentences = sentences_needed - len(content_parts)
            if remaining_sentences > 0:
                content_parts.append(f"Understanding {topic.lower()} is crucial for professionals and enthusiasts alike.")
                if remaining_sentences > 1:
                    content_parts.append(f"This analysis will provide actionable insights and practical applications.")
            
            return " ".join(content_parts)
            
        except Exception as e:
            logger.error(f"Introduction generation failed: {e}")
            return f"{topic} is an important topic that requires careful consideration and analysis."
    
    def _generate_main_content_section(self, topic: str, title: str, purpose: str, key_points: List[str], 
                                     target_words: int, writing_style: str) -> str:
        """Generate main content section"""
        try:
            content_parts = []
            
            # Section header
            content_parts.append(f"## {title}")
            content_parts.append("")
            
            # Key points elaboration
            for i, point in enumerate(key_points[:3]):  # Limit to 3 key points
                content_parts.append(f"### {point}")
                content_parts.append("")
                
                # Generate 2-3 sentences for each key point
                point_content = self._elaborate_key_point(point, topic, writing_style)
                content_parts.append(point_content)
                content_parts.append("")
            
            # Additional content to reach target length
            current_words = len(" ".join(content_parts).split())
            if current_words < target_words:
                additional_content = self._generate_additional_content(topic, title, target_words - current_words)
                content_parts.append(additional_content)
            
            return "\n".join(content_parts)
            
        except Exception as e:
            logger.error(f"Main content generation failed: {e}")
            return f"## {title}\n\nContent for this section could not be generated."
    
    def _generate_conclusion_section(self, topic: str, purpose: str, key_points: List[str], 
                                   target_words: int, writing_style: str) -> str:
        """Generate conclusion section content"""
        try:
            content_parts = []
            
            # Summary statement
            content_parts.append(f"## Conclusion")
            content_parts.append("")
            content_parts.append(f"In conclusion, {topic.lower()} presents both opportunities and challenges.")
            
            # Key takeaways
            if key_points:
                content_parts.append("Key takeaways from this analysis include:")
                for point in key_points[:3]:
                    content_parts.append(f"- {point}")
                content_parts.append("")
            
            # Future outlook
            content_parts.append("Looking ahead, the landscape of this field will continue to evolve.")
            content_parts.append("Organizations and individuals must stay informed and adaptable.")
            
            # Call to action
            content_parts.append("")
            content_parts.append("To stay competitive, consider implementing these insights and monitoring emerging trends.")
            
            return "\n".join(content_parts)
            
        except Exception as e:
            logger.error(f"Conclusion generation failed: {e}")
            return f"## Conclusion\n\nThis concludes our discussion of {topic.lower()}."
    
    def _elaborate_key_point(self, point: str, topic: str, writing_style: str) -> str:
        """Elaborate on a key point with additional context"""
        try:
            # Generate contextual sentences for the key point
            sentences = [
                f"{point} is fundamental to understanding {topic.lower()}.",
                f"This aspect influences how we approach and implement solutions in this domain.",
                f"Professionals must consider {point.lower()} when making strategic decisions."
            ]
            
            return " ".join(sentences)
            
        except Exception as e:
            logger.error(f"Key point elaboration failed: {e}")
            return f"{point} is an important consideration in this field."
    
    def _generate_additional_content(self, topic: str, title: str, additional_words: int) -> str:
        """Generate additional content to reach target word count"""
        try:
            if additional_words < 50:
                return ""
            
            # Generate contextual information
            sentences = [
                f"Understanding the broader context of {title.lower()} helps professionals make informed decisions.",
                f"This knowledge area continues to evolve with technological advancements.",
                f"Organizations that prioritize {title.lower()} often see improved outcomes and efficiency."
            ]
            
            return " ".join(sentences)
            
        except Exception as e:
            logger.error(f"Additional content generation failed: {e}")
            return ""
    
    async def optimize_content(self, content: str, target_length: int, writing_style: str) -> str:
        """Optimize content for quality and length"""
        try:
            logger.info(f"Optimizing content for {writing_style} style")
            
            # Apply style-specific optimizations
            if writing_style.lower() == "professional":
                content = self._apply_professional_style(content)
            elif writing_style.lower() == "casual":
                content = self._apply_casual_style(content)
            elif writing_style.lower() == "academic":
                content = self._apply_academic_style(content)
            
            # Optimize length
            content = self._optimize_length(content, target_length)
            
            # Improve readability
            content = self._improve_readability(content)
            
            logger.info(f"Content optimization completed")
            return content
            
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            return content
    
    def _apply_professional_style(self, content: str) -> str:
        """Apply professional writing style"""
        try:
            # Remove contractions
            content = re.sub(r"n't\b", " not", content)
            content = re.sub(r"'re\b", " are", content)
            content = re.sub(r"'s\b", " is", content)
            content = re.sub(r"'ll\b", " will", content)
            
            # Ensure proper capitalization
            content = content.replace(" i ", " I ")
            
            return content
            
        except Exception as e:
            logger.error(f"Professional style application failed: {e}")
            return content
    
    def _apply_casual_style(self, content: str) -> str:
        """Apply casual writing style"""
        try:
            # Add contractions for readability
            content = re.sub(r" is not\b", " isn't", content)
            content = re.sub(r" are not\b", " aren't", content)
            content = re.sub(r" will not\b", " won't", content)
            
            # Use active voice
            content = re.sub(r" is being\b", " is", content)
            content = re.sub(r" are being\b", " are", content)
            
            return content
            
        except Exception as e:
            logger.error(f"Casual style application failed: {e}")
            return content
    
    def _apply_academic_style(self, content: str) -> str:
        """Apply academic writing style"""
        try:
            # Ensure formal language
            content = re.sub(r"get\b", "obtain", content)
            content = re.sub(r"look at\b", "examine", content)
            content = re.sub(r"find out\b", "determine", content)
            
            # Add academic transitions
            content = re.sub(r"\. ", ". Furthermore, ", content)
            
            return content
            
        except Exception as e:
            logger.error(f"Academic style application failed: {e}")
            return content
    
    def _optimize_length(self, content: str, target_length: int) -> str:
        """Optimize content length to match target"""
        try:
            current_words = len(content.split())
            
            if current_words <= target_length:
                return content
            
            # Remove excess content while maintaining structure
            sentences = content.split('. ')
            target_sentences = max(3, int(target_length / 20))  # Assume 20 words per sentence
            
            if len(sentences) <= target_sentences:
                return content
            
            # Keep first and last sentences, remove middle ones
            kept_sentences = sentences[:target_sentences//2] + sentences[-(target_sentences//2):]
            return '. '.join(kept_sentences) + '.'
            
        except Exception as e:
            logger.error(f"Length optimization failed: {e}")
            return content
    
    def _improve_readability(self, content: str) -> str:
        """Improve content readability"""
        try:
            # Fix common issues
            content = re.sub(r'\s+', ' ', content)  # Remove extra whitespace
            content = re.sub(r'\.+', '.', content)  # Fix multiple periods
            content = re.sub(r',+', ',', content)  # Fix multiple commas
            
            # Ensure proper spacing after punctuation
            content = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', content)
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Readability improvement failed: {e}")
            return content
    
    async def finalize_content(self, content: str, topic: str, writing_style: str) -> str:
        """Finalize content with formatting and review"""
        try:
            logger.info(f"Finalizing content for topic: {topic}")
            
            # Apply final formatting
            content = self._apply_final_formatting(content)
            
            # Add metadata header
            header = self._create_content_header(topic, writing_style)
            
            # Combine header and content
            finalized_content = f"{header}\n\n{content}"
            
            logger.info(f"Content finalization completed")
            return finalized_content
            
        except Exception as e:
            logger.error(f"Content finalization failed: {e}")
            return content
    
    def _apply_final_formatting(self, content: str) -> str:
        """Apply final formatting touches"""
        try:
            # Ensure proper markdown formatting
            content = re.sub(r'^##\s+', '## ', content, flags=re.MULTILINE)
            content = re.sub(r'^###\s+', '### ', content, flags=re.MULTILINE)
            
            # Fix list formatting
            content = re.sub(r'^- ([^-])', r'- \1', content, flags=re.MULTILINE)
            
            # Ensure proper paragraph spacing
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            return content
            
        except Exception as e:
            logger.error(f"Final formatting failed: {e}")
            return content
    
    def _create_content_header(self, topic: str, writing_style: str) -> str:
        """Create content header with metadata"""
        try:
            header_parts = [
                f"# {topic}",
                "",
                f"**Writing Style:** {writing_style.title()}",
                f"**Generated:** {self._get_current_timestamp()}",
                f"**Word Count:** {len(topic.split())} (estimated)",
                ""
            ]
            
            return "\n".join(header_parts)
            
        except Exception as e:
            logger.error(f"Header creation failed: {e}")
            return f"# {topic}\n\n"
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in readable format"""
        try:
            from datetime import datetime
            return datetime.now().strftime("%B %d, %Y at %I:%M %p")
        except Exception as e:
            logger.error(f"Timestamp generation failed: {e}")
            return "Unknown" 