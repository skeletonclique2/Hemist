import requests
from typing import Dict, List
import time
from bs4 import BeautifulSoup
import re

class ContentRetriever:
    """Agent 3: Retrieve content using Search1API"""
    
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def retrieve(self, keywords: List[str]) -> Dict:
        """
        Retrieve content from multiple sources
        Args:
            keywords: List of keywords to search for
        Returns:
            Dict with retrieved content and sources
        """
        all_sources = []
        search_queries = self._prepare_search_queries(keywords)
        
        for query in search_queries[:3]:  # Limit to 3 queries to stay within free tier
            try:
                sources = self._search_with_search1api(query)
                all_sources.extend(sources)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"⚠️  Search failed for '{query}': {e}")
                continue
        
        # Process and deduplicate sources
        processed_sources = self._process_sources(all_sources)
        
        return {
            "sources": processed_sources,
            "search_queries": search_queries,
            "total_sources": len(processed_sources),
            "key_insights": self._extract_key_insights(processed_sources),
            "trending_topics": self._identify_trending_topics(processed_sources)
        }
    
    def _prepare_search_queries(self, keywords: List[str]) -> List[str]:
        """Prepare search queries from keywords"""
        queries = []
        
        # Primary keyword search
        if keywords:
            queries.append(f"{keywords[0]} latest research 2024")
            
        # Combine keywords for comprehensive search
        if len(keywords) >= 2:
            queries.append(f"{keywords[0]} {keywords[1]} trends")
            
        # News and developments
        if len(keywords) >= 1:
            queries.append(f"{keywords[0]} breakthrough news recent")
            
        return queries
    
    def _search_with_search1api(self, query: str) -> List[Dict]:
        """Search using Search1API"""
        try:
            # Updated Search1API implementation using POST with Bearer token
            url = "https://api.search1api.com/search"
            headers = {
                "Authorization": f"Bearer {self.config.SEARCH1API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "query": query,
                "search_service": "google",
                "max_results": 10,
                "language": "en"
            }
            
            print(f"🔍 Searching for: {query}")
            print(f"🔗 URL: {url}")
            print(f"🔑 Using Bearer token: {self.config.SEARCH1API_KEY[:10]}...")
            
            response = self.session.post(url, headers=headers, json=data, timeout=15)
            
            # Debug response
            print(f"📡 Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"❌ Response text: {response.text[:200]}...")
            
            response.raise_for_status()
            
            data = response.json()
            sources = []
            
            # Parse Search1API response format
            if 'results' in data:
                for result in data['results'][:5]:  # Limit to top 5 per query
                    source = {
                        'title': result.get('title', ''),
                        'url': result.get('link', ''),  # Note: 'link' not 'url'
                        'snippet': result.get('snippet', ''),
                        'domain': self._extract_domain(result.get('link', '')),
                        'relevance_score': self._calculate_relevance(result, query)
                    }
                    sources.append(source)
            else:
                print(f"⚠️  Unexpected Search1API response format: {list(data.keys())}")
            
            print(f"✅ Found {len(sources)} sources for '{query}'")
            return sources
            
        except Exception as e:
            print(f"⚠️  Search1API error for '{query}': {e}")
            return []
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc.replace('www.', '')
        except:
            return "unknown"
    
    def _calculate_relevance(self, result: Dict, query: str) -> float:
        """Calculate relevance score for a result"""
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        query_lower = query.lower()
        
        score = 0.0
        query_words = query_lower.split()
        
        # Title relevance (higher weight)
        for word in query_words:
            if word in title:
                score += 0.3
        
        # Snippet relevance
        for word in query_words:
            if word in snippet:
                score += 0.1
        
        # Domain authority bonus (simple heuristic)
        domain = result.get('url', '').lower()
        authoritative_domains = [
            'arxiv.org', 'nature.com', 'science.org', 'ieee.org',
            'mit.edu', 'stanford.edu', 'openai.com', 'deepmind.com',
            'google.com', 'microsoft.com', 'techcrunch.com'
        ]
        
        for auth_domain in authoritative_domains:
            if auth_domain in domain:
                score += 0.2
                break
        
        return min(1.0, score)
    
    def _process_sources(self, sources: List[Dict]) -> List[Dict]:
        """Process and deduplicate sources"""
        # Remove duplicates by URL
        seen_urls = set()
        unique_sources = []
        
        for source in sources:
            url = source.get('url', '')
            if url not in seen_urls and url:
                seen_urls.add(url)
                unique_sources.append(source)
        
        # Sort by relevance score
        unique_sources.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        # Clean snippets
        for source in unique_sources:
            source['snippet'] = self._clean_snippet(source.get('snippet', ''))
        
        return unique_sources[:8]  # Keep top 8 sources
    
    def _clean_snippet(self, snippet: str) -> str:
        """Clean and normalize snippet text"""
        if not snippet:
            return ""
        
        # Remove HTML tags
        snippet = re.sub(r'<[^>]+>', '', snippet)
        
        # Clean extra whitespace
        snippet = re.sub(r'\s+', ' ', snippet).strip()
        
        # Truncate if too long
        if len(snippet) > 300:
            snippet = snippet[:297] + "..."
        
        return snippet
    
    def _extract_key_insights(self, sources: List[Dict]) -> List[str]:
        """Extract key insights from sources"""
        insights = []
        
        for source in sources[:5]:  # Top 5 sources
            snippet = source.get('snippet', '')
            if snippet:
                # Simple insight extraction based on common patterns
                insight_patterns = [
                    r'(\d+%?\s+(?:increase|decrease|growth|reduction))',
                    r'(according to.*?(?:study|research|report))',
                    r'(researchers? (?:found|discovered|concluded).*?\.)',
                    r'(new (?:breakthrough|development|technology).*?\.)'
                ]
                
                for pattern in insight_patterns:
                    matches = re.findall(pattern, snippet, re.IGNORECASE)
                    insights.extend(matches[:1])  # One per pattern per source
        
        return list(set(insights))[:5]  # Remove duplicates, keep top 5
    
    def _identify_trending_topics(self, sources: List[Dict]) -> List[str]:
        """Identify trending topics from sources"""
        topics = []
        
        # Common AI/tech trending terms
        trending_terms = [
            'ChatGPT', 'GPT-4', 'LLM', 'generative AI', 'transformer',
            'neural network', 'deep learning', 'computer vision',
            'natural language processing', 'automation', 'robotics',
            'quantum computing', 'edge AI', 'MLOps', 'AI ethics'
        ]
        
        for source in sources:
            title_and_snippet = (source.get('title', '') + ' ' + source.get('snippet', '')).lower()
            
            for term in trending_terms:
                if term.lower() in title_and_snippet:
                    topics.append(term)
        
        # Count frequency and return top trending
        from collections import Counter
        topic_counts = Counter(topics)
        return [topic for topic, count in topic_counts.most_common(5)]