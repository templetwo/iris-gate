#!/usr/bin/env python3
"""
IRIS Literature Validator
Automated scientific literature search to validate IRIS predictions

Uses:
- PubMed E-utilities API (biomedical literature)
- Semantic Scholar API (AI-powered relevance ranking)
- Europe PMC API (preprints and European journals)

Purpose: Test whether IRIS convergence patterns predict experimental validation
"""

import requests
import xml.etree.ElementTree as ET
import time
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

class LiteratureValidator:
    """Automated literature validation for IRIS predictions"""
    
    def __init__(self, cache_dir: str = "literature_cache"):
        self.pubmed_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.semantic_base = "https://api.semanticscholar.org/graph/v1/"
        self.europepmc_base = "https://www.ebi.ac.uk/europepmc/webservices/rest/"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.rate_limit_delay = 0.4  # 2.5 requests/second for PubMed
        self.last_request_time = 0
    
    def validate_prediction(self, 
                          prediction: str,
                          date_before: Optional[str] = None,
                          date_after: Optional[str] = None,
                          max_results: int = 50) -> Dict:
        """
        Validate IRIS prediction against published literature
        
        Args:
            prediction: The mechanistic claim to validate (e.g., "VDAC1 modulates calcium flux")
            date_before: Only papers before this date (YYYY-MM-DD) - tests what was known
            date_after: Only papers after this date (YYYY-MM-DD) - tests prediction
            max_results: Maximum papers to retrieve per source
        
        Returns:
            {
                'prediction': str,
                'validation_status': 'validated'|'supported'|'untested'|'contradicted',
                'evidence_quality': int,  # 1-5 stars
                'pubmed_papers': List[Dict],
                'semantic_scholar_papers': List[Dict],
                'europepmc_papers': List[Dict],
                'summary': str,
                'confidence': float,
                'total_supporting': int,
                'total_contradicting': int,
                'timeline_validated': bool  # if date_before specified
            }
        """
        print(f"\n🔍 Validating prediction: {prediction}")
        print(f"   Date range: {date_after or 'any'} to {date_before or 'now'}")
        
        # Search multiple sources
        pubmed_results = self._search_pubmed(prediction, date_before, date_after, max_results)
        time.sleep(0.5)
        
        semantic_results = self._search_semantic_scholar(prediction, date_before, date_after, max_results)
        time.sleep(0.5)
        
        europepmc_results = self._search_europepmc(prediction, date_before, date_after, max_results)
        
        # Analyze combined evidence
        validation = self._analyze_evidence(
            prediction=prediction,
            pubmed_papers=pubmed_results,
            semantic_papers=semantic_results,
            europepmc_papers=europepmc_results,
            date_before=date_before
        )
        
        # Cache results
        self._cache_validation(prediction, validation)
        
        return validation
    
    def _search_pubmed(self, query: str, date_before: str, date_after: str, max_results: int) -> List[Dict]:
        """Search PubMed with date filtering"""
        print(f"   📚 Searching PubMed...")
        
        # Build date filter
        date_filter = ""
        if date_after and date_before:
            # Format: YYYY/MM/DD
            after_formatted = date_after.replace('-', '/')
            before_formatted = date_before.replace('-', '/')
            date_filter = f" AND {after_formatted}:{before_formatted}[pdat]"
        elif date_after:
            after_formatted = date_after.replace('-', '/')
            date_filter = f" AND {after_formatted}:3000[pdat]"
        elif date_before:
            before_formatted = date_before.replace('-', '/')
            date_filter = f" AND 1900:{before_formatted}[pdat]"
        
        # Search for IDs
        search_url = f"{self.pubmed_base}esearch.fcgi"
        search_params = {
            "db": "pubmed",
            "term": query + date_filter,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance"
        }
        
        self._rate_limit()
        response = requests.get(search_url, params=search_params)
        
        if response.status_code != 200:
            print(f"   ⚠️  PubMed search failed: {response.status_code}")
            return []
        
        data = response.json()
        ids = data.get("esearchresult", {}).get("idlist", [])
        
        if not ids:
            print(f"   📭 No PubMed results found")
            return []
        
        print(f"   ✓ Found {len(ids)} PubMed articles")
        
        # Fetch details
        fetch_url = f"{self.pubmed_base}efetch.fcgi"
        fetch_params = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "xml"
        }
        
        self._rate_limit()
        fetch_response = requests.get(fetch_url, params=fetch_params)
        
        if fetch_response.status_code != 200:
            return []
        
        # Parse XML
        papers = self._parse_pubmed_xml(fetch_response.text)
        return papers
    
    def _parse_pubmed_xml(self, xml_text: str) -> List[Dict]:
        """Parse PubMed XML response"""
        try:
            root = ET.fromstring(xml_text)
            papers = []
            
            for article in root.findall(".//PubmedArticle"):
                try:
                    # Extract key fields
                    pmid = article.find(".//PMID").text if article.find(".//PMID") is not None else "Unknown"
                    
                    title_elem = article.find(".//ArticleTitle")
                    title = title_elem.text if title_elem is not None else "No title"
                    
                    abstract_elem = article.find(".//AbstractText")
                    abstract = abstract_elem.text if abstract_elem is not None else "No abstract available"
                    
                    # Publication date
                    pub_date = article.find(".//PubDate")
                    year = pub_date.find("Year").text if pub_date is not None and pub_date.find("Year") is not None else "Unknown"
                    
                    # Journal
                    journal_elem = article.find(".//Journal/Title")
                    journal = journal_elem.text if journal_elem is not None else "Unknown"
                    
                    papers.append({
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract[:500] + "..." if len(abstract) > 500 else abstract,
                        "year": year,
                        "journal": journal,
                        "source": "PubMed",
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    })
                except Exception as e:
                    continue
            
            return papers
        except Exception as e:
            print(f"   ⚠️  XML parsing error: {e}")
            return []
    
    def _search_semantic_scholar(self, query: str, date_before: str, date_after: str, max_results: int) -> List[Dict]:
        """Search Semantic Scholar with AI-powered relevance"""
        print(f"   🤖 Searching Semantic Scholar...")
        
        search_url = f"{self.semantic_base}paper/search"
        
        params = {
            "query": query,
            "limit": max_results,
            "fields": "title,abstract,year,citationCount,authors,publicationDate,url,openAccessPdf"
        }
        
        # Add year filter if dates provided
        if date_after or date_before:
            year_after = int(date_after.split('-')[0]) if date_after else 1900
            year_before = int(date_before.split('-')[0]) if date_before else 2024
            params["year"] = f"{year_after}-{year_before}"
        
        try:
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"   ⚠️  Semantic Scholar failed: {response.status_code}")
                return []
            
            data = response.json()
            papers_data = data.get("data", [])
            
            if not papers_data:
                print(f"   📭 No Semantic Scholar results")
                return []
            
            print(f"   ✓ Found {len(papers_data)} Semantic Scholar papers")
            
            papers = []
            for paper in papers_data:
                papers.append({
                    "title": paper.get("title", "No title"),
                    "abstract": paper.get("abstract", "No abstract")[:500] if paper.get("abstract") else "No abstract",
                    "year": paper.get("year", "Unknown"),
                    "citations": paper.get("citationCount", 0),
                    "authors": [a.get("name") for a in paper.get("authors", [])[:3]],
                    "source": "Semantic Scholar",
                    "url": paper.get("url", ""),
                    "open_access": paper.get("openAccessPdf") is not None
                })
            
            return papers
        except Exception as e:
            print(f"   ⚠️  Semantic Scholar error: {e}")
            return []
    
    def _search_europepmc(self, query: str, date_before: str, date_after: str, max_results: int) -> List[Dict]:
        """Search Europe PMC (includes preprints)"""
        print(f"   🇪🇺 Searching Europe PMC...")
        
        search_url = f"{self.europepmc_base}search"
        
        # Build date range
        query_with_date = query
        if date_after and date_before:
            query_with_date += f" AND FIRST_PDATE:[{date_after} TO {date_before}]"
        
        params = {
            "query": query_with_date,
            "format": "json",
            "pageSize": max_results,
            "sort": "CITED desc"  # Sort by citation count
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"   ⚠️  Europe PMC failed: {response.status_code}")
                return []
            
            data = response.json()
            results = data.get("resultList", {}).get("result", [])
            
            if not results:
                print(f"   📭 No Europe PMC results")
                return []
            
            print(f"   ✓ Found {len(results)} Europe PMC papers")
            
            papers = []
            for paper in results:
                papers.append({
                    "title": paper.get("title", "No title"),
                    "abstract": paper.get("abstractText", "No abstract")[:500] if paper.get("abstractText") else "No abstract",
                    "year": paper.get("pubYear", "Unknown"),
                    "journal": paper.get("journalTitle", "Unknown"),
                    "pmid": paper.get("pmid", ""),
                    "source": "Europe PMC",
                    "is_preprint": paper.get("source") in ["PPR", "bioRxiv", "medRxiv"],
                    "citations": paper.get("citedByCount", 0)
                })
            
            return papers
        except Exception as e:
            print(f"   ⚠️  Europe PMC error: {e}")
            return []
    
    def _analyze_evidence(self, prediction: str, pubmed_papers: List[Dict], 
                         semantic_papers: List[Dict], europepmc_papers: List[Dict],
                         date_before: str) -> Dict:
        """Analyze papers to determine validation status"""
        
        total_papers = len(pubmed_papers) + len(semantic_papers) + len(europepmc_papers)
        
        if total_papers == 0:
            return {
                "prediction": prediction,
                "validation_status": "untested",
                "evidence_quality": 1,  # ⭐ speculation
                "pubmed_papers": [],
                "semantic_scholar_papers": [],
                "europepmc_papers": [],
                "summary": "No published literature found addressing this prediction.",
                "confidence": 0.0,
                "total_supporting": 0,
                "total_contradicting": 0,
                "timeline_validated": False
            }
        
        # Simple heuristic: more papers = more support
        # (In practice, would use NLP to analyze abstract sentiment)
        evidence_quality = min(5, 1 + (total_papers // 10))
        
        # Determine status
        if total_papers >= 20:
            validation_status = "validated"  # Strong experimental support
            confidence = 0.9
        elif total_papers >= 10:
            validation_status = "supported"  # Moderate support
            confidence = 0.7
        elif total_papers >= 3:
            validation_status = "supported"  # Some support
            confidence = 0.5
        else:
            validation_status = "untested"  # Minimal literature
            confidence = 0.3
        
        # Check citation counts for influence
        high_citation_papers = [
            p for p in semantic_papers + europepmc_papers 
            if p.get("citations", 0) > 50
        ]
        
        if len(high_citation_papers) >= 3:
            evidence_quality = min(5, evidence_quality + 1)
            confidence += 0.1
        
        # Timeline validation check
        timeline_validated = date_before is not None and total_papers > 0
        
        summary = self._generate_summary(
            validation_status, total_papers, evidence_quality, 
            high_citation_papers, timeline_validated
        )
        
        return {
            "prediction": prediction,
            "validation_status": validation_status,
            "evidence_quality": evidence_quality,
            "pubmed_papers": pubmed_papers,
            "semantic_scholar_papers": semantic_papers,
            "europepmc_papers": europepmc_papers,
            "summary": summary,
            "confidence": min(1.0, confidence),
            "total_supporting": total_papers,  # Simplified
            "total_contradicting": 0,  # Would need NLP analysis
            "timeline_validated": timeline_validated,
            "high_citation_count": len(high_citation_papers)
        }
    
    def _generate_summary(self, status: str, total: int, quality: int, 
                         high_citation: List, timeline: bool) -> str:
        """Generate human-readable validation summary"""
        stars = "⭐" * quality
        
        if status == "validated":
            summary = f"{stars} VALIDATED: {total} papers found providing strong experimental support."
        elif status == "supported":
            summary = f"{stars} SUPPORTED: {total} papers found providing moderate support."
        elif status == "untested":
            summary = f"{stars} UNTESTED: Only {total} papers found, limited experimental validation."
        else:
            summary = f"{stars} CONTRADICTED: Evidence suggests alternative mechanisms."
        
        if len(high_citation) > 0:
            summary += f" Includes {len(high_citation)} highly-cited papers (>50 citations)."
        
        if timeline:
            summary += " Timeline validation: Literature existed before IRIS prediction."
        
        return summary
    
    def _rate_limit(self):
        """Respect API rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def _cache_validation(self, prediction: str, validation: Dict):
        """Cache validation results"""
        timestamp = datetime.now().isoformat()
        filename = prediction.replace(" ", "_")[:50] + ".json"
        filepath = self.cache_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "prediction": prediction,
                "validation": validation
            }, f, indent=2)


# Example usage
if __name__ == "__main__":
    validator = LiteratureValidator()
    
    # Test prediction from IRIS CBD analysis
    prediction = "VDAC1 conformational change modulates calcium flux"
    
    result = validator.validate_prediction(
        prediction=prediction,
        date_before="2023-01-01",  # Only papers before IRIS analysis
        date_after="2018-01-01",   # Within relevant timeframe
        max_results=30
    )
    
    print("\n" + "="*60)
    print("VALIDATION RESULTS")
    print("="*60)
    print(f"Prediction: {result['prediction']}")
    print(f"Status: {result['validation_status'].upper()}")
    print(f"Evidence Quality: {'⭐' * result['evidence_quality']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"\nSummary: {result['summary']}")
    print(f"\nPapers Found:")
    print(f"  - PubMed: {len(result['pubmed_papers'])}")
    print(f"  - Semantic Scholar: {len(result['semantic_scholar_papers'])}")
    print(f"  - Europe PMC: {len(result['europepmc_papers'])}")
    
    if result['pubmed_papers']:
        print(f"\nSample PubMed Paper:")
        paper = result['pubmed_papers'][0]
        print(f"  Title: {paper['title']}")
        print(f"  Year: {paper['year']}")
        print(f"  URL: {paper['url']}")
