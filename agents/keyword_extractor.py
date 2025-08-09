import openai
from typing import Dict, List
import json
import tiktoken

class KeywordExtractor:
    """Agent 2: Extract SEO keywords using GPT-4 mini"""
    
    def __init__(self, config):
        self.config = config
        # Initialize OpenAI client with new SDK pattern
        self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        self.encoder = tiktoken.encoding_for_model("gpt-4o-mini")
    
    def extract(self, normalized_input: Dict) -> Dict:
        """
        Extract 5-7 relevant keywords for the topic
        Args:
            normalized_input: Output from InputNormalizer
        Returns:
            Dict with keywords and cost info
        """
        phrase = normalized_input['cleaned']
        context = normalized_input['context']
        angle = normalized_input['suggested_angle']
        
        prompt = f"""You are an SEO expert specializing in Artificial Intelligence content.

Extract 5-7 high-value SEO keywords for an article about: "{phrase}"

Context: {context}
Content Angle: {angle}

Requirements:
- Focus on AI/Technology related keywords
- Include both short-tail (1-2 words) and long-tail (3+ words) keywords
- Keywords should have good search volume potential
- Mix informational and commercial intent keywords

Return ONLY a JSON array of keywords, ranked by importance:
["keyword1", "keyword2", "keyword3", ...]

No explanation, just the JSON array."""

        try:
            # Count tokens for cost estimation
            input_tokens = len(self.encoder.encode(prompt))
            
            response = self.client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3,  # Lower temperature for consistent extraction
                response_format={"type": "json_object"}
            )
            
            # Parse response
            content = response.choices[0].message.content
            output_tokens = len(self.encoder.encode(content))
            
            # Try to parse JSON
            try:
                keywords_data = json.loads(content)
                if isinstance(keywords_data, dict) and 'keywords' in keywords_data:
                    keywords = keywords_data['keywords']
                elif isinstance(keywords_data, list):
                    keywords = keywords_data
                else:
                    # Fallback parsing
                    keywords = self._fallback_extraction(phrase)
            except json.JSONDecodeError:
                keywords = self._fallback_extraction(phrase)
            
            # Ensure we have the right number of keywords
            keywords = keywords[:self.config.MAX_KEYWORDS]
            
            # Calculate cost
            cost = self.config.estimate_cost(input_tokens, output_tokens)
            
            return {
                "keywords": keywords,
                "primary_keyword": keywords[0] if keywords else phrase.lower(),
                "secondary_keywords": keywords[1:4] if len(keywords) > 1 else [],
                "long_tail_keywords": [kw for kw in keywords if len(kw.split()) >= 3],
                "cost": cost,
                "tokens_used": input_tokens + output_tokens
            }
            
        except Exception as e:
            print(f"⚠️  Keyword extraction failed: {e}")
            # Fallback to rule-based extraction
            keywords = self._fallback_extraction(phrase)
            return {
                "keywords": keywords,
                "primary_keyword": keywords[0],
                "secondary_keywords": keywords[1:4],
                "long_tail_keywords": [],
                "cost": 0.0,
                "tokens_used": 0,
                "fallback_used": True
            }
    
    def _fallback_extraction(self, phrase: str) -> List[str]:
        """Fallback keyword extraction using rules"""
        phrase_lower = phrase.lower()
        
        # Base keywords from phrase
        base_keywords = [phrase_lower]
        
        # Add AI-related keywords based on phrase
        ai_keywords = {
            "machine learning": ["machine learning", "ML algorithms", "supervised learning"],
            "artificial intelligence": ["artificial intelligence", "AI technology", "AI applications"],
            "deep learning": ["deep learning", "neural networks", "AI models"],
            "automation": ["automation", "AI automation", "intelligent automation"],
            "data": ["data science", "big data", "data analytics"],
            "neural": ["neural networks", "artificial neural networks", "deep neural networks"]
        }
        
        # Find relevant AI keywords
        for key_phrase, related_keywords in ai_keywords.items():
            if key_phrase in phrase_lower:
                base_keywords.extend(related_keywords[:2])
                break
        
        # Add generic AI keywords if none found
        if len(base_keywords) < 5:
            base_keywords.extend([
                "artificial intelligence",
                "AI technology",
                "machine learning applications",
                "AI innovation",
                "future of AI"
            ])
        
        return base_keywords[:7]