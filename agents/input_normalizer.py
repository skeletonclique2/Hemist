import re
from typing import Dict

class InputNormalizer:
    """Agent 1: Normalize and clean input phrases"""
    
    def normalize(self, phrase: str) -> Dict:
        """
        Clean and normalize input phrase
        Args:
            phrase: Raw input phrase
        Returns:
            Dict with normalized data
        """
        # Basic cleaning
        cleaned = phrase.strip()
        cleaned = re.sub(r'\s+', ' ', cleaned)  # Multiple spaces to single
        cleaned = re.sub(r'[^\w\s-]', '', cleaned)  # Remove special chars except hyphens
        
        # Capitalize properly
        cleaned = cleaned.title()
        
        # Add AI context since that's our niche
        context_keywords = [
            "artificial intelligence", "machine learning", "deep learning",
            "neural networks", "AI", "automation", "technology", "data science"
        ]
        
        # Detect if already AI-related
        is_ai_related = any(kw.lower() in phrase.lower() for kw in context_keywords)
        
        return {
            "original": phrase,
            "cleaned": cleaned,
            "is_ai_related": is_ai_related,
            "context": "Artificial Intelligence and Technology",
            "target_length": 1500,
            "niche": "AI/Technology",
            "suggested_angle": self._suggest_angle(cleaned)
        }
    
    def _suggest_angle(self, phrase: str) -> str:
        """Suggest content angle based on phrase"""
        phrase_lower = phrase.lower()
        
        if any(word in phrase_lower for word in ["future", "trend", "prediction"]):
            return "Future predictions and trends"
        elif any(word in phrase_lower for word in ["benefit", "advantage", "help"]):
            return "Benefits and practical applications"
        elif any(word in phrase_lower for word in ["challenge", "problem", "issue"]):
            return "Challenges and solutions"
        elif any(word in phrase_lower for word in ["how", "guide", "tutorial"]):
            return "Educational guide"
        elif any(word in phrase_lower for word in ["comparison", "vs", "versus"]):
            return "Comparative analysis"
        else:
            return "Comprehensive overview"