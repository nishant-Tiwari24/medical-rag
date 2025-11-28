"""
Medical Data Collector

Fetches medical articles and information from public sources:
- PubMed Central (research articles)
- MedlinePlus (health topics)
"""

import json
import os
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup

class MedicalDataCollector:
    """
    Collects medical data from public APIs and websites.
    
    Sources:
    - PubMed Central (via E-utilities API)
    - MedlinePlus (via web scraping)
    """
    
    def __init__(self):
        """Initialize data collector."""
        self.data_dir = "medical_data"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def fetch_pubmed_articles(self, query: str, max_results: int = 50) -> List[Dict[str, str]]:
        """
        Fetch articles from PubMed Central using E-utilities API.
        
        Args:
            query: Search query
            max_results: Maximum number of articles to fetch
            
        Returns:
            List of article dictionaries
        """
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        
        # Search for articles
        search_url = f"{base_url}esearch.fcgi?db=pubmed&term={query}&retmax={max_results}&retmode=json"
        response = requests.get(search_url)
        data = response.json()
        
        if 'esearchresult' not in data or 'idlist' not in data['esearchresult']:
            return []
        
        ids = data['esearchresult']['idlist']
        
        # Fetch summaries
        articles = []
        for pmid in ids:
            summary_url = f"{base_url}esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
            summary_response = requests.get(summary_url)
            summary_data = summary_response.json()
            
            if 'result' in summary_data and pmid in summary_data['result']:
                article = summary_data['result'][pmid]
                articles.append({
                    'title': article.get('title', ''),
                    'abstract': article.get('abstract', ''),
                    'source': f"PubMed ID: {pmid}",
                    'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })
        
        return articles
    
    def fetch_medlineplus_topics(self) -> List[Dict[str, str]]:
        """
        Fetch health topics from MedlinePlus.
        
        Returns:
            List of topic dictionaries
        """
        url = "https://medlineplus.gov/healthtopics.html"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        topics = []
        for link in soup.find_all('a', href=True):
            if '/ency/' in link['href'] or link['href'].endswith('.html'):
                topics.append({
                    'title': link.text.strip(),
                    'url': f"https://medlineplus.gov{link['href']}"
                })
        
        return topics[:100]
    
    def save_data(self, data: List[Dict[str, Any]], filename: str) -> None:
        """
        Save collected data to JSON file.
        
        Args:
            data: List of data items
            filename: Output filename
        """
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(data)} items to {filepath}")
    
    def collect_all(self) -> List[Dict[str, str]]:
        """
        Collect data from all sources.
        
        Returns:
            List of all collected articles
        """
        print("Collecting medical data...")
        
        # Common medical topics
        topics = [
            "anatomy basics",
            "cardiovascular system",
            "respiratory system",
            "digestive system",
            "nervous system",
            "diabetes mellitus",
            "hypertension",
            "infectious diseases"
        ]
        
        all_articles = []
        for topic in topics:
            print(f"Fetching articles for: {topic}")
            articles = self.fetch_pubmed_articles(topic, max_results=10)
            all_articles.extend(articles)
        
        self.save_data(all_articles, "pubmed_articles.json")
        
        print("\nData collection complete!")
        return all_articles

if __name__ == "__main__":
    collector = MedicalDataCollector()
    collector.collect_all()
