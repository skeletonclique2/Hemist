#!/usr/bin/env python3
"""
AI Publishing Pipeline MVP
Generate high-quality AI articles from simple phrases
Cost: ~$0.016 per article using GPT-4-mini
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

from agents.input_normalizer import InputNormalizer
from agents.keyword_extractor import KeywordExtractor
from agents.content_retriever import ContentRetriever
from agents.duplication_checker import DuplicationChecker
from agents.article_writer import ArticleWriter
from config.settings import Config

class AIPublisher:
    def __init__(self):
        self.config = Config()
        self.cost_tracker = {"total_cost": 0.0, "articles_generated": 0}
        
        # Initialize agents
        self.normalizer = InputNormalizer()
        self.keyword_extractor = KeywordExtractor(self.config)
        self.content_retriever = ContentRetriever(self.config)
        self.duplication_checker = DuplicationChecker(self.config)
        self.writer = ArticleWriter(self.config)
        
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        
    def generate_article(self, input_phrase: str) -> Dict:
        """Main pipeline to generate article from input phrase"""
        print(f"\n🚀 Starting AI Article Generation for: '{input_phrase}'")
        print("=" * 60)
        
        start_time = time.time()
        pipeline_cost = 0.0
        
        try:
            # Agent 1: Normalize Input
            print("📝 Step 1: Normalizing input...")
            normalized = self.normalizer.normalize(input_phrase)
            print(f"✅ Input normalized: {normalized['cleaned']}")
            
            # Agent 2: Extract Keywords
            print("\n🔍 Step 2: Extracting keywords...")
            keywords_result = self.keyword_extractor.extract(normalized)
            keywords = keywords_result['keywords']
            pipeline_cost += keywords_result['cost']
            print(f"✅ Keywords extracted: {keywords}")
            
            # Agent 3: Research Content
            print("\n📚 Step 3: Researching content...")
            research = self.content_retriever.retrieve(keywords)
            print(f"✅ Research gathered: {len(research['sources'])} sources")
            
            # Agent 4: Check Duplication
            print("\n🔍 Step 4: Checking for duplicates...")
            title_result = self.duplication_checker.generate_unique_title(keywords, research)
            title = title_result['title']
            is_unique = title_result['is_unique']
            print(f"✅ Title generated: '{title}' (Unique: {is_unique})")
            
            # Agent 5: Write Article
            print("\n✍️  Step 5: Writing article...")
            article_result = self.writer.write_article(title, keywords, research)
            article = article_result['article']
            pipeline_cost += article_result['cost']
            word_count = len(article.split())
            print(f"✅ Article generated: {word_count} words")
            
            # Quality Check
            print("\n📊 Step 6: Quality assessment...")
            quality_score = self._calculate_quality_score(article, keywords)
            print(f"✅ Quality score: {quality_score}/100")
            
            # Save Article
            filename = self._save_article(article, title, {
                'keywords': keywords,
                'sources': len(research['sources']),
                'cost': pipeline_cost,
                'quality_score': quality_score,
                'processing_time': time.time() - start_time
            })
            
            # Update cost tracking
            self.cost_tracker['total_cost'] += pipeline_cost
            self.cost_tracker['articles_generated'] += 1
            
            print(f"\n🎉 Article saved: {filename}")
            print(f"💰 Cost: ${pipeline_cost:.4f}")
            print(f"⏱️  Processing time: {time.time() - start_time:.2f} seconds")
            
            return {
                'success': True,
                'filename': filename,
                'title': title,
                'word_count': word_count,
                'cost': pipeline_cost,
                'quality_score': quality_score,
                'processing_time': time.time() - start_time
            }
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'cost': pipeline_cost
            }
    
    def _calculate_quality_score(self, article: str, keywords: List[str]) -> int:
        """Calculate article quality score (0-100)"""
        score = 0
        
        # Word count check (30 points)
        word_count = len(article.split())
        if word_count >= 1500:
            score += 30
        elif word_count >= 1000:
            score += 20
        elif word_count >= 500:
            score += 10
        
        # Keyword usage (25 points)
        article_lower = article.lower()
        keyword_usage = sum(1 for kw in keywords if kw.lower() in article_lower)
        score += min(25, (keyword_usage / len(keywords)) * 25)
        
        # Structure check (25 points)
        if "##" in article:  # Has headers
            score += 10
        if "###" in article:  # Has subheaders
            score += 5
        if article.count('\n\n') >= 5:  # Has paragraphs
            score += 10
        
        # Citation check (20 points)
        citation_indicators = ['according to', 'research shows', 'study found', 'data indicates']
        citations = sum(1 for indicator in citation_indicators if indicator in article_lower)
        score += min(20, citations * 5)
        
        return min(100, score)
    
    def _save_article(self, article: str, title: str, metadata: Dict) -> str:
        """Save article to file with metadata"""
        # Create filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_').lower()[:50]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/{safe_title}_{timestamp}.md"
        
        # Prepare content
        content = f"""# {title}

*Generated by AI Publishing Pipeline*  
*Date: {datetime.now().strftime("%B %d, %Y")}*  
*Keywords: {', '.join(metadata['keywords'])}*  
*Quality Score: {metadata['quality_score']}/100*  
*Processing Time: {metadata['processing_time']:.2f}s*  
*Cost: ${metadata['cost']:.4f}*

---

{article}

---

*This article was generated using AI technology and should be reviewed before publication.*
"""
        
        # Save file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Save metadata
        metadata_file = filename.replace('.md', '_metadata.json')
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return filename
    
    def show_stats(self):
        """Show pipeline statistics"""
        print("\n📈 Pipeline Statistics")
        print("=" * 30)
        print(f"Articles generated: {self.cost_tracker['articles_generated']}")
        print(f"Total cost: ${self.cost_tracker['total_cost']:.4f}")
        if self.cost_tracker['articles_generated'] > 0:
            avg_cost = self.cost_tracker['total_cost'] / self.cost_tracker['articles_generated']
            print(f"Average cost per article: ${avg_cost:.4f}")

def main():
    """Main CLI interface"""
    print("🤖 AI Publishing Pipeline MVP")
    print("Generate high-quality articles from simple phrases")
    print("Focus: Artificial Intelligence topics")
    print("-" * 50)
    
    publisher = AIPublisher()
    
    while True:
        try:
            # Get user input
            print("\nEnter a phrase or topic (or 'quit' to exit, 'stats' for statistics):")
            user_input = input("> ").strip()
            
            if user_input.lower() == 'quit':
                publisher.show_stats()
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'stats':
                publisher.show_stats()
                continue
            elif not user_input:
                print("⚠️  Please enter a topic or phrase.")
                continue
            
            # Generate article
            result = publisher.generate_article(user_input)
            
            if result['success']:
                print(f"\n✨ Success! Check '{result['filename']}' for your article.")
            else:
                print(f"\n❌ Failed to generate article: {result.get('error', 'Unknown error')}")
                
        except KeyboardInterrupt:
            publisher.show_stats()
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()