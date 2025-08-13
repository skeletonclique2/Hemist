"""
Editing Tools for AI Agents System
Provides content analysis, fact-checking, and editing capabilities
"""

import re
from typing import Dict, Any, List, Optional
import structlog
from textstat import textstat

logger = structlog.get_logger()

class EditingTools:
    """Tools for content editing, quality analysis, and fact-checking"""
    
    def __init__(self):
        logger.info("EditingTools initialized")
    
    async def analyze_content_quality(self, content: str, topic: str) -> Dict[str, Any]:
        """Analyze content quality across multiple dimensions"""
        try:
            logger.info(f"Analyzing content quality for topic: {topic}")
            
            # Calculate various quality metrics
            readability_score = self._calculate_readability_score(content)
            topic_relevance = self._calculate_topic_relevance(content, topic)
            structure_quality = self._analyze_content_structure(content)
            content_completeness = self._analyze_content_completeness(content, topic)
            grammar_quality = self._analyze_grammar_quality(content)
            
            quality_metrics = {
                "readability_score": readability_score,
                "topic_relevance": topic_relevance,
                "structure_quality": structure_quality,
                "content_completeness": content_completeness,
                "grammar_quality": grammar_quality,
                "word_count": len(content.split()),
                "sentence_count": len(content.split('.')),
                "paragraph_count": len(content.split('\n\n')),
                "average_sentence_length": self._calculate_average_sentence_length(content)
            }
            
            logger.info(f"Content quality analysis completed")
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Content quality analysis failed: {e}")
            return {
                "readability_score": 0.5,
                "topic_relevance": 0.5,
                "structure_quality": 0.5,
                "content_completeness": 0.5,
                "grammar_quality": 0.5,
                "error": str(e)
            }
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score using textstat"""
        try:
            if not content.strip():
                return 0.0
            
            # Calculate Flesch Reading Ease
            flesch_score = textstat.flesch_reading_ease(content)
            
            # Normalize to 0-1 scale (Flesch typically ranges from 0-100)
            # Higher Flesch scores mean easier reading
            normalized_score = min(1.0, flesch_score / 100.0)
            
            # Adjust for optimal readability (60-80 is considered good)
            if 60 <= flesch_score <= 80:
                normalized_score = min(1.0, normalized_score * 1.2)
            
            return normalized_score
            
        except Exception as e:
            logger.error(f"Readability calculation failed: {e}")
            return 0.5
    
    def _calculate_topic_relevance(self, content: str, topic: str) -> float:
        """Calculate how relevant the content is to the given topic"""
        try:
            if not content or not topic:
                return 0.0
            
            # Extract key terms from topic
            topic_terms = set(re.findall(r'\b\w+\b', topic.lower()))
            topic_terms.discard('the')
            topic_terms.discard('and')
            topic_terms.discard('or')
            topic_terms.discard('in')
            topic_terms.discard('of')
            topic_terms.discard('to')
            topic_terms.discard('for')
            
            # Count topic term occurrences in content
            content_lower = content.lower()
            term_counts = {}
            total_terms = 0
            
            for term in topic_terms:
                if len(term) > 2:  # Only count meaningful terms
                    count = len(re.findall(rf'\b{re.escape(term)}\b', content_lower))
                    term_counts[term] = count
                    total_terms += count
            
            # Calculate relevance score
            if total_terms == 0:
                return 0.0
            
            # Base score from term frequency
            base_score = min(1.0, total_terms / (len(content.split()) * 0.1))
            
            # Bonus for topic term diversity
            diversity_bonus = min(0.2, len([t for t, c in term_counts.items() if c > 0]) / len(topic_terms) * 0.2)
            
            return min(1.0, base_score + diversity_bonus)
            
        except Exception as e:
            logger.error(f"Topic relevance calculation failed: {e}")
            return 0.5
    
    def _analyze_content_structure(self, content: str) -> float:
        """Analyze the structural quality of the content"""
        try:
            if not content.strip():
                return 0.0
            
            score = 0.0
            max_score = 5.0
            
            # Check for headers (## or ###)
            headers = re.findall(r'^#{2,3}\s+.+$', content, re.MULTILINE)
            if headers:
                score += 1.0
                # Bonus for multiple headers
                if len(headers) >= 3:
                    score += 0.5
            
            # Check for paragraphs (double line breaks)
            paragraphs = content.split('\n\n')
            if len(paragraphs) >= 3:
                score += 1.0
            
            # Check for lists
            if re.search(r'^[-*]\s+', content, re.MULTILINE):
                score += 0.5
            
            # Check for proper sentence structure
            sentences = content.split('.')
            if len(sentences) >= 5:
                score += 1.0
            
            # Check for balanced content distribution
            if len(content) > 500:  # Only for longer content
                score += 0.5
            
            # Check for conclusion indicators
            conclusion_indicators = ['conclusion', 'summary', 'in conclusion', 'to summarize']
            if any(indicator in content.lower() for indicator in conclusion_indicators):
                score += 0.5
            
            return min(1.0, score / max_score)
            
        except Exception as e:
            logger.error(f"Structure analysis failed: {e}")
            return 0.5
    
    def _analyze_content_completeness(self, content: str, topic: str) -> float:
        """Analyze how complete the content coverage is for the topic"""
        try:
            if not content or not topic:
                return 0.0
            
            score = 0.0
            max_score = 4.0
            
            # Check for introduction
            intro_indicators = ['introduction', 'overview', 'background', 'context']
            if any(indicator in content.lower() for indicator in intro_indicators):
                score += 1.0
            
            # Check for main content
            if len(content.split()) >= 200:  # Minimum content length
                score += 1.0
            
            # Check for examples or evidence
            example_indicators = ['example', 'for instance', 'such as', 'evidence', 'research shows']
            if any(indicator in content.lower() for indicator in example_indicators):
                score += 1.0
            
            # Check for conclusion
            conclusion_indicators = ['conclusion', 'summary', 'in conclusion', 'therefore']
            if any(indicator in content.lower() for indicator in conclusion_indicators):
                score += 1.0
            
            return min(1.0, score / max_score)
            
        except Exception as e:
            logger.error(f"Completeness analysis failed: {e}")
            return 0.5
    
    def _analyze_grammar_quality(self, content: str) -> float:
        """Analyze basic grammar and writing quality"""
        try:
            if not content.strip():
                return 0.0
            
            score = 0.0
            max_score = 4.0
            
            # Check for proper capitalization
            sentences = content.split('.')
            proper_caps = sum(1 for s in sentences if s.strip() and s.strip()[0].isupper())
            if sentences and proper_caps > 0:
                score += min(1.0, proper_caps / len(sentences))
            
            # Check for sentence endings
            proper_endings = len(re.findall(r'[.!?]\s+[A-Z]', content))
            if proper_endings > 0:
                score += min(1.0, proper_endings / len(sentences))
            
            # Check for paragraph breaks
            paragraphs = content.split('\n\n')
            if len(paragraphs) >= 2:
                score += 1.0
            
            # Check for consistent formatting
            if not re.search(r'[A-Z]{3,}', content):  # No excessive caps
                score += 0.5
            
            return min(1.0, score / max_score)
            
        except Exception as e:
            logger.error(f"Grammar analysis failed: {e}")
            return 0.5
    
    def _calculate_average_sentence_length(self, content: str) -> float:
        """Calculate average words per sentence"""
        try:
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            if not sentences:
                return 0.0
            
            total_words = sum(len(s.split()) for s in sentences)
            return total_words / len(sentences)
            
        except Exception as e:
            logger.error(f"Average sentence length calculation failed: {e}")
            return 0.0
    
    async def fact_check_content(self, content: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fact-check content against research data"""
        try:
            logger.info("Fact-checking content against research data")
            
            # Extract factual claims from content
            factual_claims = self._extract_factual_claims(content)
            
            # Check claims against research data
            verified_claims = []
            unverified_claims = []
            accuracy_score = 0.0
            
            for claim in factual_claims:
                if self._verify_claim_against_research(claim, research_data):
                    verified_claims.append(claim)
                else:
                    unverified_claims.append(claim)
            
            # Calculate accuracy score
            total_claims = len(factual_claims)
            if total_claims > 0:
                accuracy_score = len(verified_claims) / total_claims
            
            # Generate fact-check report
            fact_check_result = {
                "accuracy_score": accuracy_score,
                "total_claims": total_claims,
                "verified_claims": verified_claims,
                "unverified_claims": unverified_claims,
                "issues": self._identify_factual_issues(unverified_claims),
                "recommendations": self._generate_fact_check_recommendations(accuracy_score, unverified_claims)
            }
            
            logger.info(f"Fact-check completed: {accuracy_score:.2f} accuracy")
            return fact_check_result
            
        except Exception as e:
            logger.error(f"Fact-checking failed: {e}")
            return {
                "accuracy_score": 0.5,
                "total_claims": 0,
                "verified_claims": [],
                "unverified_claims": [],
                "issues": [],
                "recommendations": ["Fact-checking could not be completed"],
                "error": str(e)
            }
    
    def _extract_factual_claims(self, content: str) -> List[str]:
        """Extract factual claims from content"""
        try:
            claims = []
            
            # Look for statements with numbers, percentages, dates
            number_patterns = [
                r'\d+%',
                r'\d+\s+percent',
                r'\d{4}',  # Years
                r'\$\d+',
                r'\d+\s+(million|billion|trillion)',
                r'\d+\s+(years?|months?|days?)'
            ]
            
            for pattern in number_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Get the sentence containing the match
                    sentence = self._get_sentence_containing(content, match)
                    if sentence:
                        claims.append(sentence)
            
            # Look for comparative statements
            comparative_patterns = [
                r'\w+\s+is\s+\w+er\s+than',
                r'\w+\s+has\s+increased',
                r'\w+\s+has\s+decreased',
                r'\w+\s+is\s+the\s+largest',
                r'\w+\s+is\s+the\s+smallest'
            ]
            
            for pattern in comparative_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    sentence = self._get_sentence_containing(content, match)
                    if sentence:
                        claims.append(sentence)
            
            # Remove duplicates and limit to reasonable number
            unique_claims = list(set(claims))[:10]
            
            return unique_claims
            
        except Exception as e:
            logger.error(f"Factual claims extraction failed: {e}")
            return []
    
    def _get_sentence_containing(self, content: str, text: str) -> str:
        """Get the sentence containing specific text"""
        try:
            sentences = content.split('.')
            for sentence in sentences:
                if text.lower() in sentence.lower():
                    return sentence.strip()
            return ""
            
        except Exception as e:
            logger.error(f"Sentence extraction failed: {e}")
            return ""
    
    def _verify_claim_against_research(self, claim: str, research_data: Dict[str, Any]) -> bool:
        """Verify a factual claim against research data"""
        try:
            if not research_data or not claim:
                return False
            
            # Extract key terms from claim
            claim_terms = set(re.findall(r'\b\w+\b', claim.lower()))
            claim_terms.discard('the')
            claim_terms.discard('and')
            claim_terms.discard('or')
            claim_terms.discard('in')
            claim_terms.discard('of')
            claim_terms.discard('to')
            claim_terms.discard('for')
            claim_terms.discard('is')
            claim_terms.discard('are')
            claim_terms.discard('was')
            claim_terms.discard('were')
            
            # Check if claim terms appear in research data
            insights = research_data.get("insights", [])
            sources = research_data.get("sources", [])
            
            # Check insights
            for insight in insights:
                insight_lower = insight.lower()
                if any(term in insight_lower for term in claim_terms if len(term) > 3):
                    return True
            
            # Check sources
            for source in sources:
                source_text = f"{source.get('title', '')} {source.get('url', '')}".lower()
                if any(term in source_text for term in claim_terms if len(term) > 3):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Claim verification failed: {e}")
            return False
    
    def _identify_factual_issues(self, unverified_claims: List[str]) -> List[Dict[str, Any]]:
        """Identify specific factual issues"""
        try:
            issues = []
            
            for claim in unverified_claims:
                issue = {
                    "claim": claim,
                    "type": self._categorize_issue_type(claim),
                    "severity": self._assess_issue_severity(claim),
                    "suggestion": self._generate_issue_suggestion(claim)
                }
                issues.append(issue)
            
            return issues
            
        except Exception as e:
            logger.error(f"Issue identification failed: {e}")
            return []
    
    def _categorize_issue_type(self, claim: str) -> str:
        """Categorize the type of factual issue"""
        try:
            claim_lower = claim.lower()
            
            if any(word in claim_lower for word in ['%', 'percent', 'million', 'billion']):
                return "statistical_claim"
            elif any(word in claim_lower for word in ['year', 'decade', 'century']):
                return "temporal_claim"
            elif any(word in claim_lower for word in ['largest', 'smallest', 'best', 'worst']):
                return "comparative_claim"
            elif any(word in claim_lower for word in ['proven', 'demonstrated', 'established']):
                return "causal_claim"
            else:
                return "general_claim"
                
        except Exception as e:
            logger.error(f"Issue categorization failed: {e}")
            return "unknown"
    
    def _assess_issue_severity(self, claim: str) -> str:
        """Assess the severity of a factual issue"""
        try:
            claim_lower = claim.lower()
            
            # High severity: specific numbers, percentages, causal relationships
            if any(word in claim_lower for word in ['%', 'percent', 'causes', 'leads to', 'results in']):
                return "high"
            # Medium severity: comparative statements, temporal claims
            elif any(word in claim_lower for word in ['larger', 'smaller', 'before', 'after', 'during']):
                return "medium"
            # Low severity: general statements
            else:
                return "low"
                
        except Exception as e:
            logger.error(f"Issue severity assessment failed: {e}")
            return "medium"
    
    def _generate_issue_suggestion(self, claim: str) -> str:
        """Generate suggestion for addressing a factual issue"""
        try:
            issue_type = self._categorize_issue_type(claim)
            
            suggestions = {
                "statistical_claim": "Verify with recent, authoritative sources",
                "temporal_claim": "Check timeline accuracy with historical data",
                "comparative_claim": "Provide context and supporting evidence",
                "causal_claim": "Distinguish correlation from causation",
                "general_claim": "Add specific examples or citations"
            }
            
            return suggestions.get(issue_type, "Provide supporting evidence")
            
        except Exception as e:
            logger.error(f"Issue suggestion generation failed: {e}")
            return "Provide supporting evidence"
    
    def _generate_fact_check_recommendations(self, accuracy_score: float, unverified_claims: List[str]) -> List[str]:
        """Generate recommendations based on fact-check results"""
        try:
            recommendations = []
            
            if accuracy_score < 0.7:
                recommendations.append("Significant factual issues detected - review all claims")
                recommendations.append("Add citations for statistical and comparative statements")
            
            if len(unverified_claims) > 5:
                recommendations.append("High number of unverified claims - conduct additional research")
                recommendations.append("Focus on claims with high severity ratings")
            
            if accuracy_score >= 0.8:
                recommendations.append("Good factual accuracy - maintain current standards")
                recommendations.append("Consider adding more specific examples")
            
            if not recommendations:
                recommendations.append("Review content for potential factual improvements")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Fact-check recommendations generation failed: {e}")
            return ["Review content for factual accuracy"]
    
    async def improve_content_structure(self, content: str, quality_metrics: Dict[str, Any]) -> str:
        """Improve content structure based on quality metrics"""
        try:
            logger.info("Improving content structure")
            
            improved_content = content
            
            # Improve paragraph structure
            if quality_metrics.get("structure_quality", 0) < 0.7:
                improved_content = self._improve_paragraph_structure(improved_content)
            
            # Improve sentence structure
            if quality_metrics.get("readability_score", 0) < 0.7:
                improved_content = self._improve_sentence_structure(improved_content)
            
            # Add section headers if missing
            if not re.search(r'^#+\s+', improved_content, re.MULTILINE):
                improved_content = self._add_section_headers(improved_content)
            
            logger.info("Content structure improvement completed")
            return improved_content
            
        except Exception as e:
            logger.error(f"Content structure improvement failed: {e}")
            return content
    
    def _improve_paragraph_structure(self, content: str) -> str:
        """Improve paragraph structure and spacing"""
        try:
            # Fix paragraph spacing
            content = re.sub(r'\n{3,}', '\n\n', content)
            content = re.sub(r'([.!?])\s*([A-Z])', r'\1\n\n\2', content)
            
            # Ensure proper paragraph breaks
            paragraphs = content.split('\n\n')
            improved_paragraphs = []
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if len(paragraph.split()) > 100:  # Split long paragraphs
                    sentences = paragraph.split('. ')
                    if len(sentences) > 3:
                        mid_point = len(sentences) // 2
                        improved_paragraphs.extend([
                            '. '.join(sentences[:mid_point]) + '.',
                            '. '.join(sentences[mid_point:])
                        ])
                    else:
                        improved_paragraphs.append(paragraph)
                else:
                    improved_paragraphs.append(paragraph)
            
            return '\n\n'.join(improved_paragraphs)
            
        except Exception as e:
            logger.error(f"Paragraph structure improvement failed: {e}")
            return content
    
    def _improve_sentence_structure(self, content: str) -> str:
        """Improve sentence structure for better readability"""
        try:
            # Split very long sentences
            sentences = content.split('. ')
            improved_sentences = []
            
            for sentence in sentences:
                if len(sentence.split()) > 25:  # Long sentence threshold
                    # Try to split on conjunctions
                    conjunctions = [' and ', ' but ', ' or ', ' however ', ' therefore ']
                    split_sentence = sentence
                    
                    for conj in conjunctions:
                        if conj in sentence:
                            parts = sentence.split(conj)
                            if len(parts[0].split()) <= 20 and len(parts[1].split()) <= 20:
                                split_sentence = parts[0] + conj + parts[1]
                                break
                    
                    improved_sentences.append(split_sentence)
                else:
                    improved_sentences.append(sentence)
            
            return '. '.join(improved_sentences)
            
        except Exception as e:
            logger.error(f"Sentence structure improvement failed: {e}")
            return content
    
    def _add_section_headers(self, content: str) -> str:
        """Add section headers to content if missing"""
        try:
            # Simple header addition based on content structure
            paragraphs = content.split('\n\n')
            if len(paragraphs) < 3:
                return content
            
            # Add basic headers
            headers = ["Introduction", "Main Content", "Conclusion"]
            improved_content = []
            
            for i, (paragraph, header) in enumerate(zip(paragraphs, headers)):
                if i == 0:
                    improved_content.append(f"## {header}\n\n{paragraph}")
                elif i == len(paragraphs) - 1:
                    improved_content.append(f"## {header}\n\n{paragraph}")
                else:
                    improved_content.append(paragraph)
            
            return '\n\n'.join(improved_content)
            
        except Exception as e:
            logger.error(f"Section header addition failed: {e}")
            return content
    
    async def correct_factual_errors(self, content: str, issues: List[Dict[str, Any]]) -> str:
        """Correct factual errors identified during fact-checking"""
        try:
            logger.info(f"Correcting {len(issues)} factual errors")
            
            corrected_content = content
            
            for issue in issues:
                claim = issue.get("claim", "")
                suggestion = issue.get("suggestion", "")
                
                if claim and suggestion:
                    # Add clarification or correction
                    correction = f" (Note: {suggestion})"
                    corrected_content = corrected_content.replace(claim, claim + correction)
            
            logger.info("Factual error correction completed")
            return corrected_content
            
        except Exception as e:
            logger.error(f"Factual error correction failed: {e}")
            return content
    
    async def apply_editing_style(self, content: str, editing_style: str) -> str:
        """Apply specific editing style to content"""
        try:
            logger.info(f"Applying {editing_style} editing style")
            
            if editing_style.lower() == "comprehensive":
                content = self._apply_comprehensive_style(content)
            elif editing_style.lower() == "light":
                content = self._apply_light_style(content)
            elif editing_style.lower() == "academic":
                content = self._apply_academic_style(content)
            elif editing_style.lower() == "professional":
                content = self._apply_professional_style(content)
            
            logger.info(f"{editing_style} editing style applied")
            return content
            
        except Exception as e:
            logger.error(f"Editing style application failed: {e}")
            return content
    
    def _apply_comprehensive_style(self, content: str) -> str:
        """Apply comprehensive editing style"""
        try:
            # Comprehensive improvements
            content = self._improve_paragraph_structure(content)
            content = self._improve_sentence_structure(content)
            content = self._add_section_headers(content)
            content = self._polish_grammar(content)
            
            return content
            
        except Exception as e:
            logger.error(f"Comprehensive style application failed: {e}")
            return content
    
    def _apply_light_style(self, content: str) -> str:
        """Apply light editing style"""
        try:
            # Minimal improvements
            content = re.sub(r'\n{3,}', '\n\n', content)  # Fix spacing
            content = content.strip()  # Remove extra whitespace
            
            return content
            
        except Exception as e:
            logger.error(f"Light style application failed: {e}")
            return content
    
    def _apply_academic_style(self, content: str) -> str:
        """Apply academic editing style"""
        try:
            # Academic improvements
            content = self._improve_paragraph_structure(content)
            content = self._add_section_headers(content)
            content = self._polish_grammar(content)
            
            # Ensure formal language
            content = re.sub(r'get\b', 'obtain', content)
            content = re.sub(r'look at\b', 'examine', content)
            content = re.sub(r'find out\b', 'determine', content)
            
            return content
            
        except Exception as e:
            logger.error(f"Academic style application failed: {e}")
            return content
    
    def _apply_professional_style(self, content: str) -> str:
        """Apply professional editing style"""
        try:
            # Professional improvements
            content = self._improve_paragraph_structure(content)
            content = self._polish_grammar(content)
            
            # Ensure professional tone
            content = re.sub(r"n't\b", " not", content)
            content = re.sub(r"'re\b", " are", content)
            content = re.sub(r"'s\b", " is", content)
            
            return content
            
        except Exception as e:
            logger.error(f"Professional style application failed: {e}")
            return content
    
    def _polish_grammar(self, content: str) -> str:
        """Apply basic grammar improvements"""
        try:
            # Fix common grammar issues
            content = re.sub(r'\s+', ' ', content)  # Remove extra whitespace
            content = re.sub(r'\.+', '.', content)  # Fix multiple periods
            content = re.sub(r',+', ',', content)  # Fix multiple commas
            
            # Ensure proper spacing after punctuation
            content = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', content)
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Grammar polishing failed: {e}")
            return content
    
    async def polish_content(self, content: str) -> str:
        """Apply final polish to content"""
        try:
            logger.info("Applying final content polish")
            
            # Final formatting
            content = self._apply_final_formatting(content)
            
            # Ensure consistent spacing
            content = re.sub(r'\n{3,}', '\n\n', content)
            
            # Clean up any remaining issues
            content = content.strip()
            
            logger.info("Content polishing completed")
            return content
            
        except Exception as e:
            logger.error(f"Content polishing failed: {e}")
            return content
    
    def _apply_final_formatting(self, content: str) -> str:
        """Apply final formatting touches"""
        try:
            # Ensure proper markdown formatting
            content = re.sub(r'^##\s+', '## ', content, flags=re.MULTILINE)
            content = re.sub(r'^###\s+', '### ', content, flags=re.MULTILINE)
            
            # Fix list formatting
            content = re.sub(r'^- ([^-])', r'- \1', content, flags=re.MULTILINE)
            
            return content
            
        except Exception as e:
            logger.error(f"Final formatting failed: {e}")
            return content
    
    async def analyze_section_quality(self, section_content: str, section_name: str) -> Dict[str, Any]:
        """Analyze quality of a specific section"""
        try:
            logger.info(f"Analyzing section quality: {section_name}")
            
            # Basic section analysis
            word_count = len(section_content.split())
            sentence_count = len(section_content.split('.'))
            paragraph_count = len(section_content.split('\n\n'))
            
            # Calculate section-specific metrics
            readability = self._calculate_readability_score(section_content)
            content_depth = min(1.0, word_count / 100.0)  # Normalize to 0-1
            
            section_metrics = {
                "section_name": section_name,
                "word_count": word_count,
                "sentence_count": sentence_count,
                "paragraph_count": paragraph_count,
                "readability_score": readability,
                "content_depth": content_depth,
                "average_sentence_length": word_count / max(1, sentence_count)
            }
            
            logger.info(f"Section quality analysis completed for {section_name}")
            return section_metrics
            
        except Exception as e:
            logger.error(f"Section quality analysis failed: {e}")
            return {"section_name": section_name, "error": str(e)}
    
    async def fact_check_section(self, section_content: str, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fact-check a specific section"""
        try:
            logger.info("Fact-checking section content")
            
            # Extract claims from section
            claims = self._extract_claims_from_text(section_content)
            
            # Verify claims against research data
            verified_claims = []
            unverified_claims = []
            
            for claim in claims:
                if self._verify_claim_against_research(claim, research_data):
                    verified_claims.append(claim)
                else:
                    unverified_claims.append(claim)
            
            # Calculate accuracy score
            total_claims = len(claims)
            accuracy_score = len(verified_claims) / max(1, total_claims)
            
            fact_check_result = {
                "accuracy_score": accuracy_score,
                "total_claims": total_claims,
                "verified_claims": verified_claims,
                "unverified_claims": unverified_claims,
                "issues": self._identify_factual_issues(unverified_claims)
            }
            
            logger.info(f"Section fact-check completed: {accuracy_score:.2f} accuracy")
            return fact_check_result
            
        except Exception as e:
            logger.error(f"Section fact-check failed: {e}")
            return {"accuracy_score": 0.5, "error": str(e)}