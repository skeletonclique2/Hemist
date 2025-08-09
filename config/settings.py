import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for AI Publisher"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    SEARCH1API_KEY = os.getenv("SEARCH1API_KEY")
    
    # Model Settings
    OPENAI_MODEL = "gpt-4o-mini"  # Cheapest GPT-4 model

    MAX_TOKENS = 4000
    TEMPERATURE = 0.7
    
    # Search Settings
    SEARCH1API_URL = "https://api.search1api.com/search"
    MAX_SEARCH_RESULTS = 10
    
    # Content Settings
    TARGET_WORD_COUNT = 1500
    MIN_WORD_COUNT = 1000
    MAX_KEYWORDS = 7
    
    # Quality Thresholds
    MIN_QUALITY_SCORE = 60
    SIMILARITY_THRESHOLD = 0.7  # For duplicate detection
    
    # Cost Tracking
    GPT4_MINI_INPUT_COST = 0.000150  # per 1K tokens
    GPT4_MINI_OUTPUT_COST = 0.000600  # per 1K tokens
    
    def __init__(self):
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration"""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        if not self.SEARCH1API_KEY:
            raise ValueError("SEARCH1API_KEY not found in environment variables")
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for GPT-4 mini usage"""
        input_cost = (input_tokens / 1000) * self.GPT4_MINI_INPUT_COST
        output_cost = (output_tokens / 1000) * self.GPT4_MINI_OUTPUT_COST
        return input_cost + output_cost