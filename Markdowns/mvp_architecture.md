# 1-Hour MVP Architecture - AI Publishing Pipeline

## Simplified MVP Scope (AI Content Focus)

### **What We'll Build:**
✅ Input phrase → High-quality AI article (1500+ words)  
✅ Basic keyword extraction  
✅ Content research via Search1API  
✅ Article generation with GPT-4-mini  
✅ Simple duplicate checking  
✅ Local file output (Medium integration later)  
✅ Cost tracking & monitoring  

### **What We'll Skip for MVP:**
❌ Complex message bus (direct function calls)  
❌ Image generation (focus on text first)  
❌ Full Medium API integration  
❌ Advanced SEO optimization  
❌ Docker containers (single Python script)  

## Tech Stack (Ultra-Minimal)

```python
# Core Dependencies
- openai (GPT-4-mini)
- requests (Search1API)
- python-dotenv (environment variables)
- markdown (output formatting)
- sentence-transformers (similarity checking)
```

## File Structure

```
ai_publisher/
├── main.py              # Main orchestrator
├── agents/
│   ├── __init__.py
│   ├── input_normalizer.py
│   ├── keyword_extractor.py
│   ├── content_retriever.py
│   ├── duplication_checker.py
│   └── writer.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── output/              # Generated articles
├── .env                 # API keys
├── requirements.txt
└── README.md
```

## Core Agent Implementation

### **1. Input Normalizer (2 minutes)**
```python
def normalize_input(phrase: str) -> dict:
    return {
        "original": phrase,
        "cleaned": phrase.strip().title(),
        "context": "AI and Technology",
        "target_length": 1500
    }
```

### **2. Keyword Extractor (5 minutes)**
```python
def extract_keywords(normalized_input: dict) -> list:
    # Use GPT-4-mini to extract 5-7 relevant keywords
    # Cost: ~$0.001 per request
    prompt = f"Extract 5-7 SEO keywords for: {normalized_input['cleaned']}"
    # Return ranked keyword list
```

### **3. Content Retriever (8 minutes)**
```python
def retrieve_content(keywords: list) -> dict:
    # Use Search1API free tier
    # Fetch top 10 results for keyword research
    # Extract snippets and key insights
    # Cost: Free tier usage
```

### **4. Duplication Checker (5 minutes)**
```python
def check_duplication(title: str) -> bool:
    # Simple Google search via Search1API
    # Check if similar titles exist
    # Return True if unique (>70% different)
```

### **5. Article Writer (15 minutes)**
```python
def write_article(keywords: list, research: dict, title: str) -> str:
    # GPT-4-mini with optimized prompt
    # Generate 1500+ word article
    # Include citations and structure
    # Cost: ~$0.01-0.02 per article
```

## MVP Workflow (Single Script)

```python
def generate_article(input_phrase: str) -> str:
    print("🚀 Starting AI Article Generation...")
    
    # Agent 1: Normalize Input (instant)
    normalized = normalize_input(input_phrase)
    print(f"✅ Input normalized: {normalized['cleaned']}")
    
    # Agent 2: Extract Keywords (5-10 seconds)
    keywords = extract_keywords(normalized)
    print(f"✅ Keywords extracted: {keywords}")
    
    # Agent 3: Research Content (10-15 seconds)
    research = retrieve_content(keywords)
    print(f"✅ Research gathered: {len(research['sources'])} sources")
    
    # Agent 4: Check Duplication (5 seconds)
    title = generate_title(keywords)
    is_unique = check_duplication(title)
    print(f"✅ Title uniqueness: {is_unique}")
    
    # Agent 5: Write Article (30-45 seconds)
    article = write_article(keywords, research, title)
    print(f"✅ Article generated: {len(article.split())} words")
    
    # Save output
    filename = save_article(article, title)
    print(f"🎉 Article saved: {filename}")
    
    return filename
```

## Cost Estimation (Per Article)

| Service | Usage | Cost |
|---------|--------|------|
| GPT-4-mini | Keyword extraction | ~$0.001 |
| GPT-4-mini | Article writing | ~$0.015 |
| Search1API | Research queries | Free tier |
| **Total per article** | | **~$0.016** |
| **Weekly cost (3 articles)** | | **~$0.05** |
| **Monthly cost** | | **~$0.20** |

## Implementation Timeline (1 Hour)

| Minutes | Task |
|---------|------|
| 0-10 | Setup project structure, install dependencies |
| 10-20 | Implement Input Normalizer + Keyword Extractor |
| 20-35 | Build Content Retriever with Search1API |
| 35-45 | Create Duplication Checker |
| 45-55 | Implement Article Writer with GPT-4-mini |
| 55-60 | End-to-end testing + bug fixes |

## Medium Integration Notes

**Basic Medium Publishing (No Partner Program Required):**
- Medium API allows basic publishing for free
- You can post via API without Partner Program
- Partner Program only needed for monetization features
- We'll add this in Phase 2 (post-MVP)

## Quality Assurance

### **Built-in Quality Checks:**
```python
def quality_check(article: str) -> dict:
    return {
        "word_count": len(article.split()),
        "readability_score": calculate_readability(article),
        "keyword_density": check_keyword_usage(article),
        "citation_count": count_citations(article),
        "uniqueness_score": check_originality(article)
    }
```

## MVP Demo Flow

```bash
$ python main.py "Machine Learning in Healthcare"

🚀 Starting AI Article Generation...
✅ Input normalized: Machine Learning In Healthcare
✅ Keywords extracted: ['machine learning', 'healthcare AI', 'medical diagnosis', 'patient care', 'healthcare automation']
✅ Research gathered: 8 sources
✅ Title uniqueness: True
✅ Article generated: 1,847 words
💰 Cost tracking: $0.016
🎉 Article saved: output/machine_learning_healthcare_2024.md

📊 Quality Score: 87/100
- Word count: ✅ 1,847 words
- Readability: ✅ Grade 12 level
- Citations: ✅ 6 sources cited
- Uniqueness: ✅ 94% original
```

## Next Steps After MVP

1. **Test with AI topics** (your niche focus)
2. **Add Medium API integration** (15 minutes)
3. **Implement image placeholders** (10 minutes)
4. **Add basic web UI** (30 minutes)
5. **Docker containerization** (20 minutes)

---

## Ready to Start Building?

This MVP will:
- Generate high-quality 1500+ word articles
- Cost under $0.02 per article
- Work completely offline/locally
- Take 60-90 seconds per article
- Focus on AI content niche
- Provide quality metrics

**Shall we start with the implementation?** I'll create the core files and you can run them locally.