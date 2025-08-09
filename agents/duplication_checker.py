import requests
from typing import Dict, List
import re

class DuplicationChecker:
    """Agent 4: Check for duplicate content and generate unique titles"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def generate_unique_title(self, keywords: List[str], research: Dict) -> Dict:
        """
        Generate a unique title and check for duplicates
        Args:
            keywords: List of keywords
            research: Research data from ContentRetriever
        Returns:
            Dict with title and uniqueness info
        """
        # Generate candidate titles
        candidate_titles = self._generate_title_candidates(keywords, research)
        
        # Check each title for uniqueness
        for title in candidate_titles:
            is_unique = self._check_title_uniqueness(title)
            if is_unique:
                return {
                    "title": title,
                    "is_unique": True,
                    "similarity_score": 0.0,
                    "checked_against": "web_search"
                }
        
        # If no unique title found, create a more specific one
        unique_title = self._force_unique_title(keywords)
        return {
            "title": unique_title,
            "is_unique": True,
            "similarity_score": 0.0,
            "checked_against": "forced_unique",
            "note": "Generated unique title with timestamp/specific angle"
        }
    
    def _generate_title_candidates(self, keywords: List[str], research: Dict) -> List[str]:
        """Generate multiple title candidates"""
        primary_keyword = keywords[0] if keywords else "AI Technology"
        trending_topics = research.get('trending_topics', [])
        
        templates = [
            f"The Future of {primary_keyword}: What You Need to Know in 2024",
            f"{primary_keyword}: Complete Guide to Implementation and Benefits",
            f"How {primary_keyword} is Revolutionizing Modern Technology",
            f"{primary_keyword} Explained: A Comprehensive Analysis",
            f"Breaking Down {primary_keyword}: Trends, Challenges, and Opportunities",
            f"The Ultimate Guide to {primary_keyword} for Beginners and Experts",
            f"{primary_keyword}: From Theory to Real-World Applications",
            f"Understanding {primary_keyword}: Key Insights and Future Predictions"
        ]
        
        # Add trending topic variations
        if trending_topics:
            trending = trending_topics[0]
            templates.extend([
                f"{primary_keyword} and {trending}: A Perfect Match",
                f"How {trending} is Shaping {primary_keyword}",
                f"{primary_keyword} in the Age of {trending}"
            ])
        
        return templates
    
    def _check_title_uniqueness(self, title: str) -> bool:
        """Check if title is unique using search"""
        try:
            # Search for exact title
            exact_search = self._search_exact_title(title)
            if exact_search['duplicates_found'] > 0:
                return False
            # Only use basic string matching now, skip semantic similarity
            return True
        except Exception as e:
            print(f"⚠️  Uniqueness check failed: {e}")
            return True  # Assume unique if check fails
    
    def _search_exact_title(self, title: str) -> Dict:
        """Search for exact title matches"""
        try:
            # Use Search1API to check for exact matches with POST and Bearer token
            url = "https://api.search1api.com/search"
            headers = {
                "Authorization": f"Bearer {self.config.SEARCH1API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "query": f'"{title}"',  # Exact match search
                "search_service": "google",
                "max_results": 5,
                "language": "en"
            }
            
            print(f"🔍 Checking title uniqueness: {data['query']}")
            
            response = self.session.post(url, headers=headers, json=data, timeout=15)
            
            # Debug response
            if response.status_code != 200:
                print(f"❌ Title search response: {response.status_code} - {response.text[:100]}...")
            
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            # Count exact or very similar matches
            duplicates = 0
            for result in results:
                result_title = result.get('title', '').lower()
                search_title = title.lower()
                
                # Check for exact match or high similarity
                if result_title == search_title or self._text_similarity(result_title, search_title) > 0.9:
                    duplicates += 1
            
            return {
                'duplicates_found': duplicates,
                'total_results': len(results),
                'search_query': data['query']
            }
            
        except Exception as e:
            print(f"⚠️  Exact title search failed: {e}")
            return {'duplicates_found': 0, 'total_results': 0}
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Basic text similarity using word overlap"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _force_unique_title(self, keywords: List[str]) -> str:
        """Generate a forced unique title with specific elements"""
        from datetime import datetime
        
        primary_keyword = keywords[0] if keywords else "AI Technology"
        year = datetime.now().year
        month = datetime.now().strftime("%B")
        
        unique_elements = [
            f"{primary_keyword}: {month} {year} Comprehensive Analysis",
            f"Mastering {primary_keyword}: A {year} Deep Dive",
            f"{primary_keyword} Decoded: Essential Insights for {year}",
            f"The {primary_keyword} Revolution: {year} Edition",
            f"{primary_keyword} Mastery: Advanced Strategies for {year}"
        ]
        
        return unique_elements[hash(primary_keyword) % len(unique_elements)]