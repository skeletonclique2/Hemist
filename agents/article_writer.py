import openai
from typing import Dict, List
import tiktoken
import json

class ArticleWriter:
    """Agent 5: Write high-quality articles using GPT-4 mini"""
    
    def __init__(self, config):
        self.config = config
        # Initialize OpenAI client with new SDK pattern
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.encoder = tiktoken.encoding_for_model("gpt-4o-mini")
    
    def write_article(self, title: str, keywords: List[str], research: Dict) -> Dict:
        """
        Write a comprehensive article
        Args:
            title: Article title
            keywords: List of keywords to include
            research: Research data from ContentRetriever
        Returns:
            Dict with article content and metadata
        """
        try:
            # Prepare context from research
            context = self._prepare_research_context(research)
            
            # Generate article using GPT-4 mini
            article_result = self._generate_article_content(title, keywords, context)
            
            # Post-process article
            final_article = self._post_process_article(article_result['content'], keywords)
            
            return {
                "article": final_article,
                "word_count": len(final_article.split()),
                "cost": article_result['cost'],
                "tokens_used": article_result['tokens_used'],
                "sections_generated": self._count_sections(final_article),
                "keywords_included": self._count_keyword_usage(final_article, keywords)
            }
            
        except Exception as e:
            print(f"❌ Article writing failed: {e}")
            # Return a basic fallback article
            fallback_article = self._generate_fallback_article(title, keywords)
            return {
                "article": fallback_article,
                "word_count": len(fallback_article.split()),
                "cost": 0.0,
                "tokens_used": 0,
                "fallback_used": True
            }
    
    def _prepare_research_context(self, research: Dict) -> str:
        """Prepare research context for the prompt"""
        context_parts = []
        
        # Add key insights
        if research.get('key_insights'):
            context_parts.append("Key Insights:")
            for insight in research['key_insights'][:3]:
                context_parts.append(f"- {insight}")
        
        # Add trending topics
        if research.get('trending_topics'):
            context_parts.append("\nTrending Topics:")
            context_parts.append(f"- {', '.join(research['trending_topics'][:3])}")
        
        # Add source snippets
        if research.get('sources'):
            context_parts.append("\nRelevant Information:")
            for source in research['sources'][:5]:
                if source.get('snippet'):
                    context_parts.append(f"- {source['snippet'][:200]}...")
        
        return '\n'.join(context_parts)
    
    def _generate_article_content(self, title: str, keywords: List[str], context: str) -> Dict:
        """Generate article content using GPT-4 mini"""
        
        primary_keyword = keywords[0] if keywords else "artificial intelligence"
        secondary_keywords = keywords[1:4] if len(keywords) > 1 else []
        
        prompt = f"""You are an expert technology writer specializing in artificial intelligence and emerging technologies. Write a comprehensive, engaging article with the following specifications:

TITLE: {title}

TARGET KEYWORDS:
Primary: {primary_keyword}
Secondary: {', '.join(secondary_keywords)}

RESEARCH CONTEXT:
{context}

REQUIREMENTS:
1. Write 1,500-2,000 words
2. Use engaging, professional tone suitable for Medium audience
3. Include proper markdown formatting with headers (##, ###)
4. Naturally incorporate all target keywords
5. Structure with clear introduction, body sections, and conclusion
6. Include data points and insights from the research context
7. Add practical examples and real-world applications
8. Use subheadings for better readability
9. Include a compelling call-to-action at the end
10. Focus on AI/technology niche with current trends

ARTICLE STRUCTURE:
## Introduction
- Hook the reader with compelling opening
- Introduce the main topic and its importance
- Preview what the article will cover

## Main Content Sections (3-4 sections)
- Use descriptive subheadings
- Include practical examples
- Reference current trends and developments
- Incorporate research insights naturally

## Conclusion
- Summarize key points
- Discuss future implications
- Include call-to-action

Write the complete article now, ensuring high quality and engagement throughout."""

        try:
            # Count input tokens
            input_tokens = len(self.encoder.encode(prompt))
            
            # Generate article
            response = self.client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.config.MAX_TOKENS,
                temperature=self.config.TEMPERATURE
            )
            
            content = response.choices[0].message.content
            output_tokens = len(self.encoder.encode(content))
            
            # Calculate cost
            cost = self.config.estimate_cost(input_tokens, output_tokens)
            
            return {
                "content": content,
                "cost": cost,
                "tokens_used": input_tokens + output_tokens,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens
            }
            
        except Exception as e:
            print(f"❌ GPT-4 article generation failed: {e}")
            raise e
    
    def _post_process_article(self, article: str, keywords: List[str]) -> str:
        """Post-process the generated article"""
        
        # Ensure proper markdown formatting
        article = self._fix_markdown_formatting(article)
        
        # Add keyword density optimization
        article = self._optimize_keyword_usage(article, keywords)
        
        # Add meta information
        article = self._add_reading_metadata(article)
        
        return article
    
    def _fix_markdown_formatting(self, article: str) -> str:
        """Fix and standardize markdown formatting"""
        import re
        
        # Ensure headers have proper spacing
        article = re.sub(r'\n(#{1,3})\s*', r'\n\n\1 ', article)
        
        # Ensure paragraphs are properly separated
        article = re.sub(r'\n\n\n+', '\n\n', article)
        
        # Fix list formatting
        article = re.sub(r'\n-\s*', '\n\n- ', article)
        article = re.sub(r'\n(\d+)\.\s*', r'\n\n\1. ', article)  # Fixed: added capture group around \d+
        
        return article.strip()
    
    def _optimize_keyword_usage(self, article: str, keywords: List[str]) -> str:
        """Optimize keyword usage in the article"""
        # This is a simplified version - in production, you'd want more sophisticated NLP
        
        word_count = len(article.split())
        target_density = 0.02  # 2% keyword density
        
        for keyword in keywords[:3]:  # Focus on top 3 keywords
            current_occurrences = article.lower().count(keyword.lower())
            target_occurrences = max(1, int(word_count * target_density))
            
            if current_occurrences < target_occurrences:
                # Could add more sophisticated keyword insertion here
                pass
        
        return article
    
    def _add_reading_metadata(self, article: str) -> str:
        """Add reading time and other metadata"""
        word_count = len(article.split())
        reading_time = max(1, word_count // 200)  # Average reading speed
        
        metadata = f"*Reading time: {reading_time} minutes | Word count: {word_count}*\n\n"
        
        return metadata + article
    
    def _count_sections(self, article: str) -> int:
        """Count the number of sections in the article"""
        import re
        headers = re.findall(r'^#{2,3}\s+.+$', article, re.MULTILINE)
        return len(headers)
    
    def _count_keyword_usage(self, article: str, keywords: List[str]) -> Dict:
        """Count keyword usage in the article"""
        article_lower = article.lower()
        usage = {}
        
        for keyword in keywords:
            count = article_lower.count(keyword.lower())
            usage[keyword] = count
        
        return usage
    
    def _generate_fallback_article(self, title: str, keywords: List[str]) -> str:
        """Generate a basic fallback article when GPT fails"""
        primary_keyword = keywords[0] if keywords else "artificial intelligence"
        
        fallback_template = f"""# {title}

*This is a fallback article generated when the main AI writing system encountered an issue.*

## Introduction

{primary_keyword} represents one of the most significant technological advances of our time. As we continue to explore its potential, understanding its implications becomes increasingly important for businesses, researchers, and individuals alike.

## Understanding {primary_keyword}

{primary_keyword} encompasses a broad range of technologies and applications that are reshaping how we interact with digital systems. From automation to predictive analytics, these technologies are becoming integral to modern operations.

### Key Applications

The applications of {primary_keyword} span across multiple industries:

- **Healthcare**: Improving diagnostic accuracy and treatment personalization
- **Finance**: Enhancing fraud detection and risk assessment
- **Transportation**: Enabling autonomous vehicles and traffic optimization
- **Education**: Personalizing learning experiences and automating administrative tasks

## Current Trends and Developments

The field continues to evolve rapidly, with new breakthroughs emerging regularly. Recent developments focus on:

1. Improved efficiency and accuracy
2. Better integration with existing systems
3. Enhanced user experience and accessibility
4. Ethical considerations and responsible implementation

## Future Implications

As {primary_keyword} continues to mature, we can expect to see:

- Increased adoption across various sectors
- More sophisticated applications and use cases
- Greater emphasis on ethical guidelines and governance
- Continued innovation in underlying technologies

## Conclusion

{primary_keyword} represents a transformative force in technology. By staying informed about its developments and implications, we can better prepare for a future where these technologies play an increasingly central role in our daily lives.

Understanding and adapting to these changes will be crucial for success in the digital age.

---

*This article provides a basic overview of {primary_keyword}. For more detailed and current information, please refer to recent research and industry publications.*"""

        return fallback_template