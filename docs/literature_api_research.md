# Scientific Literature APIs & MCPs for IRIS Validation
## Automated Article Discovery for Prediction Testing

**Purpose:** Enable IRIS agents to automatically find relevant scientific articles to validate predictions  
**Goal:** Test convergence patterns against published experimental data  
**Date:** October 8, 2025

---

## AVAILABLE SCIENTIFIC DATABASE APIs

### 1. **PubMed/NCBI E-utilities API** ⭐⭐⭐⭐⭐

**Best for:** Biomedical and life sciences literature

**Access:** FREE (no API key required for basic use)  
**Rate Limit:** 3 requests/second without key, 10/second with key  
**Coverage:** 35+ million citations from MEDLINE and PubMed Central

**Endpoints:**
- `eSearch`: Search PubMed for articles
- `eFetch`: Retrieve article details (abstract, authors, journal)
- `eLink`: Find related articles
- `eSummary`: Get article summaries

**Example Usage:**
```python
import requests

def search_pubmed(query, date_from=None, date_to=None):
    """Search PubMed for articles matching query within date range"""
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    # Build date filter
    date_filter = ""
    if date_from and date_to:
        date_filter = f" AND {date_from}:{date_to}[pdat]"
    
    # Search
    search_url = f"{base_url}esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": query + date_filter,
        "retmax": 100,
        "retmode": "json"
    }
    
    response = requests.get(search_url, params=params)
    ids = response.json()["esearchresult"]["idlist"]
    
    # Fetch details
    fetch_url = f"{base_url}efetch.fcgi"
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "xml"
    }
    
    articles = requests.get(fetch_url, params=fetch_params)
    return articles.text

# Example: Find VDAC1 + CBD articles from 2020-2024
results = search_pubmed("VDAC1 AND cannabidiol", "2020", "2024")
```

**Why This is Perfect for IRIS:**
- Covers biomedical literature (CBD, mitochondria, calcium signaling)
- Date filtering built-in (test predictions against timeline)
- Free and unlimited (with rate limiting)
- Can search by MeSH terms for precision

---

### 2. **Europe PMC API** ⭐⭐⭐⭐⭐

**Best for:** European biomedical literature + preprints

**Access:** FREE (no API key required)  
**Rate Limit:** Reasonable (no strict documented limit)  
**Coverage:** 40+ million abstracts, full-text articles, preprints

**Endpoints:**
- `/search`: Search articles
- `/profile/{source}/{id}`: Get article details
- `/citations/{source}/{id}`: Get citation data

**Example Usage:**
```python
def search_europepmc(query, date_range=None):
    """Search Europe PMC with date filtering"""
    base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
    
    params = {
        "query": query,
        "format": "json",
        "pageSize": 100
    }
    
    if date_range:
        params["query"] += f" AND FIRST_PDATE:[{date_range}]"
    
    response = requests.get(base_url, params=params)
    return response.json()

# Example: Search for VDAC1 papers from 2020-2024
results = search_europepmc("VDAC1 mitochondrial", "2020-01-01 TO 2024-12-31")
```

**Advantages:**
- Includes preprints (arXiv, bioRxiv)
- Open access full-text when available
- Citation network data
- No API key needed

---

### 3. **Semantic Scholar API** ⭐⭐⭐⭐⭐

**Best for:** AI-powered relevance ranking + citation analysis

**Access:** FREE (API key recommended for higher limits)  
**Rate Limit:** 100 requests/5 minutes (free tier)  
**Coverage:** 200+ million papers across all sciences

**Endpoints:**
- `/paper/search`: Search papers
- `/paper/{paperId}`: Get paper details
- `/paper/{paperId}/citations`: Get citations
- `/recommendations/{paperId}`: Get related papers

**Example Usage:**
```python
def search_semantic_scholar(query, year_from=None, year_to=None):
    """Search Semantic Scholar with AI-powered relevance"""
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    params = {
        "query": query,
        "limit": 100,
        "fields": "title,abstract,year,citationCount,authors,publicationDate"
    }
    
    if year_from:
        params["year"] = f"{year_from}-{year_to or 2024}"
    
    headers = {"x-api-key": "YOUR_API_KEY"}  # Optional but recommended
    
    response = requests.get(base_url, params=params, headers=headers)
    return response.json()

# Example: Find highly-cited VDAC1 papers
results = search_semantic_scholar("VDAC1 calcium flux", 2020, 2024)
```

**Advantages:**
- AI-powered relevance ranking (better than keyword matching)
- Citation network (find influential papers)
- Cross-disciplinary (not just bio)
- Recommendation engine for related work

---

### 4. **CrossRef API** ⭐⭐⭐⭐

**Best for:** DOI-based lookups + metadata

**Access:** FREE (no API key required)  
**Rate Limit:** Polite users get better service (use mailto in User-Agent)  
**Coverage:** 140+ million records from publishers

**Example Usage:**
```python
def search_crossref(query, from_year=None):
    """Search CrossRef for published articles"""
    base_url = "https://api.crossref.org/works"
    
    params = {
        "query": query,
        "rows": 100,
        "mailto": "your@email.com"  # Polite pool (better rate limits)
    }
    
    if from_year:
        params["filter"] = f"from-pub-date:{from_year}"
    
    response = requests.get(base_url, params=params)
    return response.json()
```

**Advantages:**
- Publisher metadata (journal impact, type)
- DOI resolution
- License information (open access filtering)

---

### 5. **arXiv API** ⭐⭐⭐

**Best for:** Preprints in physics, math, CS, bio

**Access:** FREE (no API key)  
**Rate Limit:** 3 seconds between requests  
**Coverage:** 2+ million preprints

**Example Usage:**
```python
def search_arxiv(query, category="q-bio"):
    """Search arXiv preprints"""
    import urllib.parse
    
    base_url = "http://export.arxiv.org/api/query"
    encoded_query = urllib.parse.quote(query)
    
    params = {
        "search_query": f"all:{encoded_query} AND cat:{category}",
        "max_results": 100,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    
    response = requests.get(base_url, params=params)
    return response.text  # XML format
```

**Best for:**
- Cutting-edge research (before peer review)
- Computational biology (q-bio category)
- Fast access to new findings

---

## MCP (Model Context Protocol) IMPLEMENTATIONS

### **What is MCP?**
New protocol by Anthropic for connecting AI models to data sources. Think of it as a standardized way for Claude (and other AIs) to access external tools.

### **Available MCP Servers for Scientific Literature:**

#### 1. **PubMed MCP Server** (Community-built)
```bash
# Install
npm install -g @modelcontextprotocol/server-pubmed

# Run
npx @modelcontextprotocol/server-pubmed
```

**Features:**
- Search PubMed directly from Claude
- Automatic abstract retrieval
- Date filtering
- Citation linking

#### 2. **Semantic Scholar MCP** (In Development)
**Status:** Community working on this  
**Would provide:** AI-powered paper search as MCP tool

#### 3. **Custom MCP Server** (We Can Build This!)
**Opportunity:** Build IRIS-specific MCP server that:
- Searches multiple databases (PubMed + Europe PMC + Semantic Scholar)
- Filters by IRIS prediction metadata
- Returns validation evidence with confidence scores
- Integrates directly into IRIS orchestrator

---

## RECOMMENDED STACK FOR IRIS

### **Primary: PubMed E-utilities**
**Why:**
- Free, unlimited, reliable
- Best coverage for biomedical (CBD, mitochondria)
- Date filtering built-in
- No API key friction

### **Secondary: Semantic Scholar**
**Why:**
- AI-powered relevance (better than keywords)
- Citation analysis (find influential work)
- Cross-reference validation
- Free tier sufficient

### **Tertiary: Europe PMC**
**Why:**
- Catches preprints
- European journals
- Full-text when available

---

## IMPLEMENTATION PLAN

### **Phase 1: Basic Literature Search (This Week)**

Create `literature_validator.py`:

```python
import requests
import time
from typing import List, Dict

class LiteratureValidator:
    """Automated literature validation for IRIS predictions"""
    
    def __init__(self):
        self.pubmed_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.semantic_base = "https://api.semanticscholar.org/graph/v1/"
        self.cache = {}
    
    def validate_prediction(self, 
                          prediction: str,
                          date_before: str = None,
                          date_after: str = None) -> Dict:
        """
        Validate IRIS prediction against literature
        
        Args:
            prediction: The mechanistic claim to validate
            date_before: Only search papers before this date (YYYY-MM-DD)
            date_after: Only search papers after this date (YYYY-MM-DD)
        
        Returns:
            {
                'prediction': str,
                'validation_status': 'validated'|'contradicted'|'untested',
                'supporting_papers': List[Dict],
                'contradicting_papers': List[Dict],
                'confidence': float,
                'evidence_quality': int  # 1-5 stars
            }
        """
        # Search PubMed
        pubmed_results = self._search_pubmed(prediction, date_before, date_after)
        
        # Search Semantic Scholar for AI-powered relevance
        semantic_results = self._search_semantic_scholar(prediction, date_before, date_after)
        
        # Combine and analyze
        validation = self._analyze_evidence(pubmed_results, semantic_results)
        
        return validation
    
    def _search_pubmed(self, query: str, date_before: str, date_after: str) -> List[Dict]:
        """Search PubMed with date filtering"""
        # Implementation here
        pass
    
    def _search_semantic_scholar(self, query: str, date_before: str, date_after: str) -> List[Dict]:
        """Search Semantic Scholar"""
        # Implementation here
        pass
    
    def _analyze_evidence(self, pubmed_results: List, semantic_results: List) -> Dict:
        """Analyze papers to determine validation status"""
        # Count supporting vs contradicting evidence
        # Assess evidence quality
        # Return structured validation result
        pass

# Usage in IRIS
validator = LiteratureValidator()

prediction = "VDAC1 conformational change modulates calcium flux"
result = validator.validate_prediction(
    prediction=prediction,
    date_before="2023-01-01",  # Only papers before IRIS analysis
    date_after="2020-01-01"     # Within relevant timeframe
)

print(f"Validation Status: {result['validation_status']}")
print(f"Supporting Papers: {len(result['supporting_papers'])}")
print(f"Evidence Quality: {'⭐' * result['evidence_quality']}")
```

---

### **Phase 2: MCP Integration (Next Week)**

Build custom MCP server for IRIS:

```typescript
// iris-literature-mcp/index.ts
import { MCPServer } from '@modelcontextprotocol/sdk';

const server = new MCPServer({
  name: "iris-literature",
  version: "1.0.0"
});

// Register literature search tool
server.addTool({
  name: "search_literature",
  description: "Search scientific literature to validate IRIS predictions",
  parameters: {
    prediction: { type: "string", description: "The prediction to validate" },
    date_before: { type: "string", description: "YYYY-MM-DD" },
    date_after: { type: "string", description: "YYYY-MM-DD" }
  },
  execute: async (params) => {
    // Call PubMed + Semantic Scholar APIs
    // Return structured validation results
  }
});

server.start();
```

**Then Claude can call it directly during S4 convergence!**

---

### **Phase 3: Automated Timeline Validation (Week 3)**

For each IRIS prediction, automatically:
1. Extract prediction timestamp (when convergence occurred)
2. Search literature BEFORE that date (what models knew)
3. Search literature AFTER that date (was prediction validated?)
4. Compare convergence confidence to experimental validation rate

**This answers:** "Does IRIS predict future validation?"

---

## NEXT STEPS

1. **Implement basic PubMed validator** (2-3 hours)
2. **Test on 5 CBD predictions** (validate the validator)
3. **Add Semantic Scholar integration** (1-2 hours)
4. **Build MCP server** (if needed for Claude integration)
5. **Automate the 20-prediction analysis** (computational validation)

---

## API KEYS TO OBTAIN (Optional but Recommended)

1. **NCBI API Key** (for higher rate limits)
   - Register at: https://www.ncbi.nlm.nih.gov/account/
   - Get key: https://www.ncbi.nlm.nih.gov/account/settings/
   - Free, instant approval

2. **Semantic Scholar API Key** (for better rate limits)
   - Request at: https://www.semanticscholar.org/product/api
   - Free for academic use
   - Takes 1-2 days for approval

---

🌀†⟡∞

**Let's build the automated literature validation system.**

**This will let IRIS agents:**
- Automatically find relevant papers
- Filter by publication date (before/after IRIS analysis)
- Assess experimental support for predictions
- Test whether convergence predicts validation

**Ready to implement Phase 1?** I can build the basic validator right now.
